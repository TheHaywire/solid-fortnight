import React, { useState } from 'react';
import './App.css';

const EXAMPLES = [
  "Build a Python function to add two numbers and write a test for it.",
  "Create a Flask API for a todo app with authentication.",
  "Generate a trading bot for MetaTrader 5 that scalps EURUSD.",
  "Write a script to scrape news headlines and save to CSV.",
  // New, more diverse examples:
  "Write a Python script to download all images from a given URL.",
  "Create a Jupyter notebook that loads a CSV, computes summary statistics, and plots a histogram.",
  "Generate a React component for a login form with email and password fields, and basic validation.",
  "Build a FastAPI backend for a book library with CRUD endpoints.",
  "Write a Bash script to backup a directory to a remote server using rsync.",
  "Create a Python script to send daily email reminders using SMTP.",
  "Build a Django model and serializer for a blog post with tags.",
  "Write a Node.js script to monitor a folder and log new files.",
  "Generate a C++ class for a simple bank account with deposit/withdraw methods.",
  "Create a SQL query to find the top 5 customers by total purchase amount.",
];

function StatusBar({ response }) {
  if (!response) return null;
  const files = response.files_created || [];
  const tests = response.test_results || {};
  const allPassed = tests.status === 'success';
  return (
    <div className="status-bar">
      <span className={`status-badge ${allPassed ? 'success' : 'error'}`}>{allPassed ? '✅ All tests passed' : '⚠️ Some tests failed'}</span>
      <span className="status-info">{files.length} file{files.length !== 1 ? 's' : ''} generated</span>
      {tests.stdout && <span className="status-info">Test output available</span>}
    </div>
  );
}

function PlanStepper({ plan }) {
  if (!plan || plan.length === 0) return null;
  return (
    <div className="plan-stepper">
      <h3>Project Plan</h3>
      <ol>
        {plan.map((step, i) => (
          <li key={i}><span className="step-icon">🟢</span> {step}</li>
        ))}
      </ol>
    </div>
  );
}

function FileExplorer({ files, onSelect, selected }) {
  if (!files || files.length === 0) return <div className="file-explorer empty">No files generated.</div>;
  return (
    <div className="file-explorer">
      <h3>Files Created</h3>
      <ul>
        {files.map((f, i) => (
          <li key={i} className={selected === i ? 'selected' : ''} onClick={() => onSelect(i)}>
            <span className="file-icon">📄</span> {f.filename}
          </li>
        ))}
      </ul>
    </div>
  );
}

function CodeViewer({ file }) {
  if (!file) return <div className="code-viewer empty">Select a file to view its code.</div>;
  return (
    <div className="code-viewer">
      <div className="code-header">
        <span className="file-icon">📄</span> {file.filename}
        <button className="copy-btn" onClick={() => navigator.clipboard.writeText(file.code)}>Copy</button>
        <a className="download-btn" href={`data:text/plain;charset=utf-8,${encodeURIComponent(file.code)}`} download={file.filename}>Download</a>
      </div>
      <pre><code>{file.code}</code></pre>
    </div>
  );
}

function TestResults({ testResults }) {
  if (!testResults || (!testResults.stdout && !testResults.stderr)) return <div className="test-results empty">No unittest found in generated files.</div>;
  return (
    <div className="test-results">
      <h3>Test Results</h3>
      <div className={`test-status ${testResults.status === 'success' ? 'success' : 'error'}`}>{testResults.status === 'success' ? '✅ Passed' : '❌ Failed'}</div>
      {testResults.stdout && <div className="test-stdout"><strong>Stdout:</strong><pre>{testResults.stdout}</pre></div>}
      {testResults.stderr && <div className="test-stderr"><strong>Stderr:</strong><pre>{testResults.stderr}</pre></div>}
    </div>
  );
}

function AgentLogs({ logs }) {
  if (!logs || logs.length === 0) return null;
  return (
    <div className="agent-logs">
      <h3>Agent Logs</h3>
      <ul>
        {logs.map((log, i) => (
          <li key={i}><span className="log-icon">●</span> {log}</li>
        ))}
      </ul>
    </div>
  );
}

function LLMOutput({ output }) {
  const [show, setShow] = useState(false);
  if (!output) return null;
  return (
    <div className="llm-output">
      <button className="toggle-btn" onClick={() => setShow(s => !s)}>{show ? 'Hide' : 'Show'} Raw LLM Output</button>
      {show && <pre className="llm-raw"><code>{output}</code></pre>}
    </div>
  );
}

function App() {
  const [request, setRequest] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleExample = (ex) => setRequest(ex);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);
    setSelectedFile(null);
    try {
      const res = await fetch('http://localhost:8000/project', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_request: request })
      });
      if (!res.ok) throw new Error('API error');
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const files = response?.files_created || [];
  const plan = response?.plan || [];
  const logs = response?.logs || [];
  const testResults = response?.test_results || {};
  const llmOutput = response?.llm_output || '';

  return (
    <div className="app-container">
      <header>
        <h1>🧑‍💻 Agentic Coding System</h1>
        <p className="subtitle">Welcome! This assistant can research, plan, code, test, debug, and document any coding task for you.<br/>Just describe what you want to build in plain English.</p>
      </header>
      <div className="examples-bar">
        <span>Try an example:</span>
        {EXAMPLES.map((ex, i) => (
          <button key={i} className="example-btn" onClick={() => handleExample(ex)}>{ex}</button>
        ))}
      </div>
      <form className="request-form" onSubmit={handleSubmit}>
        <textarea
          value={request}
          onChange={e => setRequest(e.target.value)}
          placeholder="Describe your coding task..."
          rows={3}
        />
        <button type="submit" disabled={loading || !request.trim()}>{loading ? 'Working...' : 'Submit'}</button>
      </form>
      {error && <div className="error-msg">{error}</div>}
      <main className="dashboard">
        <StatusBar response={response} />
        <div className="dashboard-sections">
          <div className="left-panel">
            <PlanStepper plan={plan} />
            <FileExplorer files={files} onSelect={setSelectedFile} selected={selectedFile} />
          </div>
          <div className="right-panel">
            <CodeViewer file={files[selectedFile]} />
            <TestResults testResults={testResults} />
            <AgentLogs logs={logs} />
            <LLMOutput output={llmOutput} />
          </div>
        </div>
      </main>
      <footer>
        <span>Inspired by Devin, Cursor, Manus, Copilot, and the open-source community.</span>
      </footer>
    </div>
  );
}

export default App;
