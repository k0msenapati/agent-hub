<p align="center">
    <img alt="hero" width="450" src="https://emoji-route.deno.dev/svg/🤖" />
</p>

> [!NOTE]
> 
> Agent Hub is an AI collaboration platform designed to transform your data into intelligent AI agents. With Agent Hub, you can unlock powerful insights and automate tasks effortlessly by creating tailored AI agents, building comprehensive knowledge bases, and managing your data files seamlessly.

## 🌟 Features

> **Agent Hub** features intro:

- **AI Agents** – Create and manage AI agents tailored to your specific needs for intelligent responses.
- **Knowledge Bases** – Build comprehensive knowledge bases from your data for efficient querying and insights.
- **File Management** – Upload and organize your files to integrate seamlessly with AI processes.

## 💻 Installation

Follow these steps to set up and run Agent Hub:

1. **Setup MindsDB and Ollama with Docker** (docker-compose.yml is provided):

   ```bash
   docker-compose up -d
   ```

2. **Install nomic-embed-text in Ollama container**:

   ```bash
   docker exec ollama ollama add nomic-embed-text
   ```

3. **Create KB Summarizer Model in MindsDB container** (visit MindsDB GUI at http://localhost:47334):

   ```sql
   -- Create a MindsDB engine for Groq
   CREATE ML_ENGINE groq_engine
   FROM groq
   USING
         groq_api_key = "groq_api_key_here";  # Replace with your actual Groq API key

   -- Create a MindsDB model for summarizing knowledge base content
   CREATE MODEL kb_summarizer
   PREDICT summary
   USING
      engine = 'groq_engine',
      model_name = 'gemma2-9b-it',
      prompt_template = 'Summarize the following knowledge base content concisely and highlight key insights:\n\n{{kb_content}}\n\nSummary:';
   ```

4. **Clone the Repository**:

   ```bash
   git clone https://github.com/k0msenapati/agent-hub.git
   ```

5. **Navigate to the Project Directory**:

   ```bash
   cd agent-hub
   ```

6. **Create a Virtual Environment**:

   ```bash
   uv venv
   ```

7. **Activate the Virtual Environment**:

   ```bash
   source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
   ```

8. **Install Dependencies**:

   ```bash
   uv add python-dotenv flask flask-sqlalchemy flask-migrate flask-bcrypt flask-login mindsdb_sdk
   ```

9. **Initialize Database**:

   ```bash
   flask db init
   ```

10. **Migrate Database**:

    ```bash
    flask db migrate
    ```

11. **Upgrade Database**:

    ```bash
    flask db upgrade
    ```

12. **Run the Application**:

    ```bash
    uv run run.py
    ```

---

<!-- 
## 📷 Screenshots

> Here's a working and expected screenshot of Agent Hub



| Landing Page  |
|------------|
| ![Demo](https://github.com/ArnavK-09.png) |
 -->

---


## 👤 Author

<table>
  <tbody>
    <tr>
        <td align="center" valign="top" width="14.28%"><a href="https://github.com/k0msenapati"><img src="https://github.com/k0msenapati.png?s=100" width="130px;" alt="K Om Senapati"/></a><br /><a href="https://github.com/k0msenapati"><h4><b>K Om Senapati</b></h3></a></td>
    </tr>
  </tbody>
</table>

---

<h2 align="center">📄 License</h2>

<p align="center">
<strong>Agent Hub</strong> is licensed under the <code>Unlicense</code> License. See the <a href="https://github.com/k0msenapati/agent-hub/blob/main/LICENSE">LICENSE</a> file for more details.
</p>

---

<p align="center">
    <strong>🌟 If you find this project helpful, please give it a star on GitHub! 🌟</strong>
</p>
