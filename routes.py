from flask import render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from models import (
    User,
    Project,
    File,
    KnowledgeBase,
    Agent,
    AgentKnowledgeBase,
    Chat,
    Analytics,
)
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import pandas as pd
from mindsdb.agent import ModelConfig, create_agent, delete_agent, query_agent
from mindsdb.file import create_file, delete_file, get_file, list_files
from mindsdb.summary import summarize_kb
from mindsdb.kb import (
    KnowledgeBaseConfig,
    OllamaEmbeddingModel,
    create_knowledge_base,
    delete_knowledge_base,
    ingest_data,
    query_knowledge_base,
)


def register_routes(app, db, bcrypt):
    @app.route("/")
    def index():
        return render_template("index.html", user=current_user)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("dashboard"))
            flash("Invalid username or password")
        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            username = request.form["username"]
            name = request.form["name"]
            password = request.form["password"]
            email = request.form["email"]
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = User(
                name=name, username=username, email=email, password=hashed_password
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                # Create a default project for the user in both local DB and MindsDB
                project_name = f"{username}_project"
                new_project = Project(name=project_name, user_id=new_user.uid)
                db.session.add(new_project)
                db.session.commit()
                # Create project in MindsDB
                from mindsdb import server

                server.create_project(project_name)
                return redirect(url_for("login"))
            except IntegrityError:
                db.session.rollback()
                flash("Username or email already exists")
            except Exception as e:
                db.session.rollback()
                flash(f"Error creating project: {str(e)}")
        return render_template("signup.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user
        project = Project.query.filter_by(user_id=user.uid).first()
        files = File.query.filter_by(user_id=user.uid).all()
        kbs = KnowledgeBase.query.filter_by(user_id=user.uid).all()
        agents = Agent.query.filter_by(user_id=user.uid).all()
        from mindsdb.datasource import list_datasources
        datasources = list_datasources(user.username)
        
        analytics_data = Analytics.query.filter_by(user_id=user.uid).all()
        analytics_object = {
            "file_upload": 0,
            "kb_query": 0,
            "agent_query": 0,
        }
        for analytic in analytics_data:
            if analytic.event_type in analytics_object:
                analytics_object[analytic.event_type] = analytic.event_count
        
        return render_template(
            "dashboard.html",
            user=user,
            project=project,
            files=files,
            kbs=kbs,
            agents=agents,
            datasources=datasources,
            analytics=analytics_object,
        )

    @app.route("/upload_file", methods=["GET", "POST"])
    @login_required
    def upload_file():
        if request.method == "POST":
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["file"]
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file:
                try:
                    # Read file into DataFrame based on file type
                    if str(file.filename).endswith(".csv"):
                        df = pd.read_csv(file) # type: ignore
                        file_name = str(file.filename).rsplit(".csv", 1)[0]
                    elif str(file.filename).endswith(".json"):
                        df = pd.read_json(file) # type: ignore
                        file_name = str(file.filename).rsplit(".json", 1)[0]
                    else:
                        flash("Unsupported file type. Only CSV and JSON are supported.")
                        return redirect(request.url)

                    # Prefix filename with username
                    username = current_user.username
                    prefixed_filename = f"{username}_{file_name}"

                    # Create file in MindsDB
                    create_file(file_name=prefixed_filename, df=df)

                    # Save file metadata to database
                    new_file = File(
                        filename=prefixed_filename, # type: ignore
                        original_filename=file.filename, # type: ignore
                        user_id=current_user.uid, # type: ignore
                    )
                    db.session.add(new_file)

                    # Update analytics
                    analytics = Analytics.query.filter_by(
                        user_id=current_user.uid, event_type="file_upload"
                    ).first()
                    if analytics:
                        analytics.event_count += 1
                        analytics.last_event = datetime.utcnow()
                    else:
                        analytics = Analytics(
                            user_id=current_user.uid, event_type="file_upload" # type: ignore
                        )
                        db.session.add(analytics)

                    db.session.commit()
                    flash(f"File {file.filename} uploaded successfully")
                    return redirect(url_for("dashboard"))
                except Exception as e:
                    flash(f"Error uploading file: {str(e)}")
                    return redirect(request.url)
        return render_template("upload_file.html")

    @app.route("/view_file/<int:file_id>")
    @login_required
    def view_file(file_id):
        file = File.query.get_or_404(file_id)
        if file.user_id != current_user.uid:
            flash("Unauthorized access")
            return redirect(url_for("dashboard"))
        file_content = get_file(file.filename)
        return render_template("view_file.html", file=file, file_content=file_content)

    @app.route("/delete_file/<int:file_id>")
    @login_required
    def delete_file_route(file_id):
        file = File.query.get_or_404(file_id)
        if file.user_id != current_user.uid:
            flash("Unauthorized access")
            return redirect(url_for("dashboard"))
        try:
            delete_file(file.filename)
            db.session.delete(file)
            db.session.commit()
            flash(f"File {file.original_filename} deleted successfully")
        except Exception as e:
            flash(f"Error deleting file: {str(e)}")
        return redirect(url_for("dashboard"))

    @app.route("/create_kb", methods=["GET", "POST"])
    @login_required
    def create_kb():
        if request.method == "POST":
            name = request.form["name"]
            embedding_model_provider = request.form["embedding_model_provider"]
            embedding_model_name = request.form["embedding_model_name"]
            embedding_model_base_url = request.form.get("embedding_model_base_url", "")
            metadata_columns = request.form.get("metadata_columns", "")
            content_columns = request.form.get("content_columns", "")
            id_column = request.form["id_column"]
            file_id = request.form.get("file_id", "")
            project = Project.query.filter_by(user_id=current_user.uid).first()

            try:
                # Create KB in MindsDB
                kb_config = KnowledgeBaseConfig(
                    name=name,
                    embedding_model=OllamaEmbeddingModel(
                        provider=embedding_model_provider, # type: ignore
                        model_name=embedding_model_name,
                        base_url=embedding_model_base_url
                        or "http://host.docker.internal:11434",
                    ),
                    metadata_columns=(
                        metadata_columns.split(",") if metadata_columns else []
                    ),
                    content_columns=(
                        content_columns.split(",") if content_columns else []
                    ),
                    id_column=id_column,
                )
                create_knowledge_base(kb_config, project_name=project.name)

                # Save KB metadata to database
                new_kb = KnowledgeBase(
                    name=name,
                    user_id=current_user.uid,
                    project_id=project.id,
                    embedding_model_provider=embedding_model_provider,
                    embedding_model_name=embedding_model_name,
                    embedding_model_base_url=embedding_model_base_url,
                    metadata_columns=metadata_columns,
                    content_columns=content_columns,
                    id_column=id_column,
                )
                db.session.add(new_kb)
                db.session.commit()

                # Ingest data if a file is selected
                if file_id:
                    file = File.query.get_or_404(int(file_id))
                    if file.user_id != current_user.uid:
                        flash("Unauthorized access to file")
                        return redirect(request.url)
                    ingest_data(
                        kb_name=name,
                        table_name=f"files.{file.filename}",
                        project_name=project.name,
                    )
                    flash(
                        f"Knowledge Base {name} created and data from {file.original_filename} ingested successfully"
                    )
                else:
                    flash(f"Knowledge Base {name} created successfully")
                return redirect(url_for("dashboard"))
            except Exception as e:
                flash(f"Error creating KB or ingesting data: {str(e)}")
                return redirect(request.url)
        files = File.query.filter_by(user_id=current_user.uid).all()
        return render_template("create_kb.html", files=files)

    @app.route("/get_file_columns/<int:file_id>", methods=["GET"])
    @login_required
    def get_file_columns(file_id):
        file = File.query.get_or_404(file_id)
        if file.user_id != current_user.uid:
            return jsonify({"error": "Unauthorized access"}), 403
        try:
            file_content = get_file(file.filename)
            if file_content is not None and hasattr(file_content, "columns"):
                columns = file_content.columns.tolist()
                return jsonify({"columns": columns})
            else:
                return (
                    jsonify({"error": "File content not available or has no columns"}),
                    404,
                )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/ingest_to_kb/<int:kb_id>", methods=["POST"])
    @login_required
    def ingest_to_kb(kb_id):
        kb = KnowledgeBase.query.get_or_404(kb_id)
        if kb.user_id != current_user.uid:
            flash("Unauthorized access")
            return redirect(url_for("dashboard"))
        file_id = request.form["file_id"]
        file = File.query.get_or_404(file_id)
        if file.user_id != current_user.uid:
            flash("Unauthorized access")
            return redirect(url_for("dashboard"))
        project = Project.query.filter_by(user_id=current_user.uid).first()
        try:
            ingest_data(
                kb_name=kb.name,
                table_name=f"files.{file.filename}",
                project_name=project.name,
            )
            flash(f"Data from {file.original_filename} ingested into {kb.name}")
        except Exception as e:
            flash(f"Error ingesting data: {str(e)}")
        return redirect(url_for("view_kb", kb_id=kb_id))

    @app.route("/view_kb/<int:kb_id>")
    @login_required
    def view_kb(kb_id):
        kb = KnowledgeBase.query.get_or_404(kb_id)
        if kb.user_id != current_user.uid:
            flash("Unauthorized access")
            return redirect(url_for("dashboard"))
        return render_template("view_kb.html", kb=kb)

    @app.route("/query_kb/<int:kb_id>", methods=["POST"])
    @login_required
    def query_kb(kb_id):
        kb = KnowledgeBase.query.get_or_404(kb_id)
        if kb.user_id != current_user.uid:
            return jsonify({"error": "Unauthorized access"}), 403
        results = None
        project = Project.query.filter_by(user_id=current_user.uid).first()
        query_text = request.form.get("query_text", "")
        relevance = float(request.form.get("relevance", 0.5))
        metadata_filter = request.form.get("metadata_filter", "")
        try:
            results = query_knowledge_base(
                kb.name,
                query_text,
                relevance,
                metadata_filter,
                project_name=project.name,
            )
            # Update analytics
            analytics = Analytics.query.filter_by(
                user_id=current_user.uid, event_type="kb_query"
            ).first()
            if analytics:
                analytics.event_count += 1
                analytics.last_event = datetime.utcnow()
            else:
                analytics = Analytics(
                    user_id=current_user.uid, event_type="kb_query"
                )
                db.session.add(analytics)
            db.session.commit()
            # Convert DataFrame to JSON serializable format
            if results is not None and not results.empty:
                results_json = results.to_dict(orient="records")
            else:
                results_json = []
            return jsonify({"results": results_json})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/summarize_kb/<int:kb_id>", methods=["POST"])
    @login_required
    def summarize_kb_route(kb_id):
        kb = KnowledgeBase.query.get_or_404(kb_id)
        if kb.user_id != current_user.uid:
            return jsonify({"error": "Unauthorized access"}), 403
        project = Project.query.filter_by(user_id=current_user.uid).first()
        content = request.form.get("content", "")
        try:
            summary = summarize_kb(
                project_name=project.name, kb_name=kb.name, content=content
            )
            return jsonify({"summary": summary})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/delete_kb/<int:kb_id>")
    @login_required
    def delete_kb(kb_id):
        kb = KnowledgeBase.query.get_or_404(kb_id)
        if kb.user_id != current_user.uid:
            flash("Unauthorized access")
            return redirect(url_for("dashboard"))
        project = Project.query.filter_by(user_id=current_user.uid).first()
        try:
            delete_knowledge_base(kb.name, project_name=project.name)
            db.session.delete(kb)
            db.session.commit()
            flash(f"Knowledge Base {kb.name} deleted successfully")
        except Exception as e:
            flash(f"Error deleting KB: {str(e)}")
        return redirect(url_for("dashboard"))

    @app.route("/create_agent", methods=["GET", "POST"])
    @login_required
    def create_new_agent():
        if request.method == "POST":
            name = request.form["name"]
            model_provider = request.form["model_provider"]
            model_name = request.form["model_name"]
            api_key = request.form.get("api_key", "")
            system_prompt = request.form.get("system_prompt", "")
            kb_ids = request.form.getlist("kb_ids")
            project = Project.query.filter_by(user_id=current_user.uid).first()

            try:
                # If API key is empty, try to get it from environment
                if not api_key:
                    import os
                    from dotenv import load_dotenv

                    load_dotenv()
                    api_key = os.getenv("API_KEY", "")

                # Create agent in MindsDB
                model_config = ModelConfig(
                    provider=model_provider,
                    model_name=model_name,
                    api_key=api_key,
                    system_prompt=system_prompt,
                )
                kb_names = []
                for kb_id in kb_ids:
                    kb = KnowledgeBase.query.get_or_404(int(kb_id))
                    if kb.user_id != current_user.uid:
                        flash("Unauthorized access to KB")
                        return redirect(request.url)
                    kb_names.append(f"{project.name}.{kb.name}")
                create_agent(
                    agent_name=name,
                    model_config=model_config,
                    knowledge_bases=kb_names,
                    project_name=project.name,
                )

                # Save agent metadata to database
                new_agent = Agent(
                    name=name,
                    user_id=current_user.uid,
                    project_id=project.id,
                    model_provider=model_provider,
                    model_name=model_name,
                    api_key=api_key,
                    system_prompt=system_prompt,
                )
                db.session.add(new_agent)
                db.session.flush()
                for kb_id in kb_ids:
                    assoc = AgentKnowledgeBase(
                        agent_id=new_agent.id, knowledge_base_id=int(kb_id)
                    )
                    db.session.add(assoc)
                db.session.commit()
                flash(f"Agent {name} created successfully")
                return redirect(url_for("dashboard"))
            except Exception as e:
                flash(f"Error creating agent: {str(e)}")
                return redirect(request.url)
        kbs = KnowledgeBase.query.filter_by(user_id=current_user.uid).all()
        return render_template("create_agent.html", kbs=kbs)

    @app.route("/view_agent/<int:agent_id>")
    @login_required
    def view_agent(agent_id):
        agent = Agent.query.get_or_404(agent_id)
        if agent.user_id != current_user.uid:
            flash("Unauthorized access")
            return redirect(url_for("dashboard"))
        chats = (
            Chat.query.filter_by(agent_id=agent_id)
            .order_by(Chat.timestamp.desc())
            .all()
        )
        return render_template("view_agent.html", agent=agent, chats=chats)

    @app.route("/chat_with_agent/<int:agent_id>", methods=["POST"])
    @login_required
    def chat_with_agent(agent_id):
        agent = Agent.query.get_or_404(agent_id)
        if agent.user_id != current_user.uid:
            return jsonify({"error": "Unauthorized access"}), 403
        message = request.json.get("message", "")
        project = Project.query.filter_by(user_id=current_user.uid).first()
        try:
            response = query_agent(agent.name, message, project_name=project.name)
            new_chat = Chat(
                user_id=current_user.uid,
                agent_id=agent_id,
                message=message,
                response=response,
            )
            db.session.add(new_chat)
            # Update analytics
            analytics = Analytics.query.filter_by(
                user_id=current_user.uid, event_type="agent_query"
            ).first()
            if analytics:
                analytics.event_count += 1
                analytics.last_event = datetime.utcnow()
            else:
                analytics = Analytics(
                    user_id=current_user.uid, event_type="agent_query"
                )
                db.session.add(analytics)
            db.session.commit()
            print(f"Chat with agent {agent.name}: {message} -> {response}")
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/delete_agent/<int:agent_id>")
    @login_required
    def delete_agent_route(agent_id):
        agent = Agent.query.get_or_404(agent_id)
        if agent.user_id != current_user.uid:
            flash("Unauthorized access")
            return redirect(url_for("dashboard"))
        project = Project.query.filter_by(user_id=current_user.uid).first()
        try:
            delete_agent(agent.name, project_name=project.name)
            db.session.delete(agent)
            db.session.commit()
            flash(f"Agent {agent.name} deleted successfully")
        except Exception as e:
            flash(f"Error deleting agent: {str(e)}")
        return redirect(url_for("dashboard"))

    @app.route('/create_datasource', methods=['GET', 'POST'])
    @login_required
    def create_datasource_route():
        if request.method == 'POST':
            name = request.form.get('name', '')
            engine = request.form.get('engine', '')
            host = request.form.get('host', '')
            port = request.form.get('port', '')
            database = request.form.get('database', '')
            user = request.form.get('user', '')
            password = request.form.get('password', '')
            schema = request.form.get('schema', '')

            if not name or not engine:
                flash("Name and engine are required fields for data source creation.", 'error')
                return redirect(url_for('create_datasource_route'))

            parameters = {
                "host": host,
                "port": port,
                "database": database,
                "user": user,
                "password": password
            }
            if schema:
                parameters["schema"] = schema

            try:
                from mindsdb.datasource import create_datasource
                create_datasource(name, engine, parameters, current_user.username)
                flash(f"Data Source '{name}' created successfully!", 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f"Error creating data source: {str(e)}", 'error')
                return redirect(url_for('create_datasource_route'))

        return render_template('create_datasource.html')

    @app.route('/delete_datasource/<string:datasource_name>', methods=['GET'])
    @login_required
    def delete_datasource_route(datasource_name):
        try:
            from mindsdb.datasource import delete_datasource
            delete_datasource(datasource_name, current_user.username)
            flash(f"Data Source '{datasource_name}' deleted successfully!", 'success')
        except Exception as e:
            flash(f"Error deleting data source: {str(e)}", 'error')
        return redirect(url_for('dashboard'))

    @app.route('/view_datasource/<string:datasource_name>', methods=['GET'])
    @login_required
    def view_datasource(datasource_name):
        try:
            from mindsdb.datasource import list_tables, list_columns
            tables = list_tables(datasource_name, current_user.username)
            table_details = []
            for table in tables:
                columns = list_columns(table, datasource_name, current_user.username)
                table_details.append({'name': table, 'columns': columns})
            return render_template('view_datasource.html', datasource_name=datasource_name, table_details=table_details)
        except Exception as e:
            flash(f"Error viewing data source: {str(e)}", 'error')
            return redirect(url_for('dashboard'))
