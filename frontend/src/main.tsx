import React, {useEffect, useState} from "react";
import {createRoot} from "react-dom/client";
import Editor from "@monaco-editor/react";
import "./style.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const examples: Record<string,string> = {
  python: `name = input()
print(f"Hello, {name}!")`,
  c: `#include <stdio.h>
int main(void){
    char name[100];
    scanf("%99s", name);
    printf("Hello, %s!\\n", name);
    return 0;
}`,
  cpp: `#include <iostream>
#include <string>
int main(){
    std::string name;
    std::cin >> name;
    std::cout << "Hello, " << name << "!\\n";
}`,
  javascript: `const name = require("fs").readFileSync(0,"utf8").trim();
console.log("Hello, " + name + "!");`,
  typescript: `const name: string = require("fs").readFileSync(0, "utf8").trim();
console.log("Hello, " + name + "!");`,
  java: `import java.util.*;
class Main {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        System.out.println("Hello, " + input.nextLine() + "!");
    }
}`,
  go: `package main
import "fmt"
func main(){
    var name string
    fmt.Scanln(&name)
    fmt.Println("Hello, " + name + "!")
}`,
  rust: `use std::io;
fn main(){
    let mut name = String::new();
    io::stdin().read_line(&mut name).unwrap();
    println!("Hello, {}!", name.trim());
}`,
  php: `<?php
$name = trim(fgets(STDIN));
echo "Hello, {$name}!\\n";
?>`
};

function App(){
  const [language,setLanguage]=useState("python");
  const [code,setCode]=useState(examples.python);
  const [stdin,setStdin]=useState("CodeForge");
  const [runId,setRunId]=useState("");
  const [result,setResult]=useState<any>(null);
  const [running,setRunning]=useState(false);
  const [error,setError]=useState("");

  useEffect(()=>setCode(examples[language] || "// Write your code here"),[language]);

  async function run(){
    setRunning(true); setResult(null); setError("");
    try {
      const r=await fetch(`${API}/api/v1/runs`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({language,source:code,stdin})});
      const accepted=await r.json();
      if (!r.ok) throw new Error(accepted.detail || "The run could not be submitted.");
      setRunId(accepted.id);
      for (let attempt = 0; attempt < 100; attempt++) {
        await new Promise(x=>setTimeout(x,300));
        const rr=await fetch(`${API}/api/v1/runs/${accepted.id}`);
        const data=await rr.json();
        if (!rr.ok) throw new Error(data.detail || "The run result could not be loaded.");
        setResult(data);
        if (["finished","compile_error","runtime_error","runner_error","timeout"].includes(data.status)) return;
      }
      throw new Error("The run exceeded the polling limit.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "The run failed.");
    } finally {
      setRunning(false);
    }
  }

  const status = error ? "Request failed" : result?.status || (running ? "Running" : "Ready");
  const isFailure = Boolean(error || result?.status?.includes("error") || result?.status === "timeout");
  const displayOutput = error || result?.stderr || result?.stdout || (result ? result.status : "Run your program to see output.");

  return <main className="app-shell">
    <header className="topbar">
      <div className="brand-lockup">
        <div className="brand-mark">CF</div>
        <div><h1>CodeForge</h1><p>Compile. Run. Iterate.</p></div>
      </div>
    </header>

    <section className="control-bar">
      <div className="control-group"><label className="language-control"><span>Language</span><select value={language} onChange={e=>setLanguage(e.target.value)}>
          {["python","c","cpp","java","javascript","typescript","go","rust","php"].map(x=><option key={x}>{x}</option>)}
        </select></label><button className="run-button" onClick={run} disabled={running}><span>{running ? "..." : "▶"}</span>{running ? "Running" : "Run code"}</button></div>
      <div className={`run-status ${isFailure ? "status-failure" : status === "finished" ? "status-success" : ""}`}><span className="status-dot" />{status}<span className="run-id">{runId ? `#${runId.slice(0,8)}` : "No run yet"}</span></div>
    </section>

    <div className="ide-layout">
      <nav className="project-sidebar" aria-label="Project files">
        <div className="sidebar-title"><span>EXPLORER</span><button aria-label="More project actions">...</button></div>
        <div className="project-name"><span className="folder-icon">▾</span> codeforge-project</div>
        <button className="file-row active-file"><span className="file-icon">{language === "python" ? "PY" : language.slice(0,2).toUpperCase()}</span><span>main.{language === "javascript" ? "js" : language === "typescript" ? "ts" : language === "python" ? "py" : language}</span></button>
        <div className="sidebar-spacer" />
      </nav>
      <div className="ide-main">
        <div className="workspace-tabs"><span className="active-tab"><span className="file-icon">{language === "python" ? "PY" : language.slice(0,2).toUpperCase()}</span> main.{language === "javascript" ? "js" : language === "typescript" ? "ts" : language === "python" ? "py" : language}</span><span className="tab-close">×</span></div>
        <div className="workspace">
          <section className="panel editor-panel">
        <div className="panel-heading"><div><span className="panel-kicker">Source</span><strong>main.{language === "javascript" ? "js" : language === "typescript" ? "ts" : language === "python" ? "py" : language}</strong></div></div>
        <div className="editor"><Editor height="100%" theme="vs-dark" language={language === "cpp" ? "cpp" : language} value={code} onChange={v=>setCode(v||"")} options={{fontSize:14,lineHeight:22,minimap:{enabled:false},automaticLayout:true,padding:{top:14}}}/></div>
          </section>
          <aside className="side-column">
        <section className="panel input-panel"><div className="panel-heading"><div><span className="panel-kicker">Input</span><strong>stdin</strong></div><span className="character-count">{stdin.length} chars</span></div><textarea aria-label="Standard input" value={stdin} onChange={e=>setStdin(e.target.value)} placeholder="Enter input for your program..." /></section>
        <section className="panel output-panel"><div className="panel-heading"><div><span className="panel-kicker">Result</span><strong>Output</strong></div>{result?.duration_ms != null && <span className="character-count">{result.duration_ms} ms</span>}</div><pre className={isFailure ? "error" : ""}>{displayOutput}</pre>{result && <div className="result-footer"><span>Exit code <b>{result.exit_code ?? "-"}</b></span><span>Status <b>{result.status}</b></span></div>}</section>
          </aside>
        </div>
      </div>
    </div>
    <footer className="app-footer"><span>Created by Harsh Nagar</span><a className="github-link" href="https://github.com/Harsh0675" target="_blank" rel="noreferrer" aria-label="Open Harsh Nagar's GitHub profile" title="GitHub profile"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .5a12 12 0 0 0-3.79 23.39c.6.11.82-.26.82-.58v-2.03c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.74.08-.74 1.2.09 1.83 1.23 1.83 1.23 1.07 1.83 2.8 1.3 3.48 1 .11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.34-5.47-5.94 0-1.31.47-2.38 1.23-3.22-.12-.3-.53-1.52.12-3.17 0 0 1-.32 3.3 1.23a11.5 11.5 0 0 1 6.01 0c2.29-1.55 3.29-1.23 3.29-1.23.66 1.65.25 2.87.13 3.17.76.84 1.22 1.91 1.22 3.22 0 4.61-2.8 5.63-5.48 5.93.43.37.82 1.1.82 2.22v3.29c0 .32.22.7.83.58A12 12 0 0 0 12 .5Z"/></svg><span>GitHub</span></a></footer>
  </main>
}
createRoot(document.getElementById("root")!).render(<App/>);
