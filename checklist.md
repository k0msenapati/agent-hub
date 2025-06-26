# Checklist for Quest 19

### **🛠️ [40 pts] Build an app with KBs**  

Build a functional application (CLI, Web App, API, Bot Interface etc.) where the primary interaction or feature relies on the semantic query results from the KB. To claim these points make sure:

- [x] Your app executes [🔗 `CREATE KNOWLEDGE_BASE`](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#create-knowledge-base-syntax)
- [x] Your app ingests data using [🔗 `INSERT INTO knowledge_base`](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#insert-into-syntax)
- [x] Your app retrieves relevant data based on on semantic queries [🔗 `SELECT ... FROM ... WHERE content LIKE '<query>'`](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#select-from-kb-syntax)
- [x] Your app uses [🔗 `CREATE INDEX ON KNOWLEDGE_BASE`](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#create-index-on-knowledge-base-syntax)

---

### **🛠️ [10 pts]  Use metadata columns**  

- [x] Define [🔗 `metadata_columns`](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#metadata-columns) during ingestion and use `WHERE` clauses that combine semantic search with SQL attribute filtering on `metadata_columns`.

---

### **🛠️ [10 pts] Integrate JOBS**

- [x] Set up a [🔗 `MindsDB JOB`](https://docs.mindsdb.com/rest/jobs/create#create-a-job) that periodically checks a data source and inserts *new* data into the KB (using LAST or similar logic).

---

### **🛠️ [10 pts] Integrate with AI Tables or Agents** 

- [x] Build a multi-step workflow within MindsDB by taking the results from a KB semantic query and feeding them as input into another [🔗 `MindsDB AI Table`](https://docs.mindsdb.com/generative-ai-tables#what-are-generative-ai-tables) (e.g., for summarisation, classification, generation).

---

### **✍️ [30 pts] Upload a video and write a nice README**  

You can claim this if:

- [x] You upload a short video demo explaining the app & showcasing the KB interaction.
- [x] Your project has a `README.md` with clear setup instructions.

---

### **✍️ [5 pts] Document the process and showcase your app** 

- [x] Write an article on DevTo, HashNode, Medium, or any blogging platform of your choice to document how you built this app and to showcase the practical product use cases for these features.

---

### **✍️ [5 pts] Give feedback and suggest features**

- [x] You submit the [🔗 Product Feedback Form](https://quira-org.typeform.com/to/magewvh9). Extra points might be given here if you suggest really good features 😉

<!-- ---

### **🍒 [up to 20 pts] Project Quality**  

Projects that collect at least 85 points will be reviewed by [@Chandre](https://x.com/Chan_vdw) from the MindsDB team will reward up to 20 more points based on the quality of the app. -->

---

### **🎁 [10 pts] Integreate `CREATE Agent`**

- [x] Projects that integrate [`CREATE Agent`](https://docs.mindsdb.com/mindsdb_sql/agents/agent) will be rewarded with an additional 10 points.

---

### **🎁  [10 pts] Secret Challenge #2**

- [x] Use [`EVALUATE KNOWLEDGE_BASE`](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#evaluate-knowledge-base-syntax) to evaluate the relevancy and accuracy of the documents and data returned by the knowledge base.

