LANGUAGES = {
    "python": {
        "image": "codeforge-runner-python",
        "file": "main.py",
        "compile": None,
        "run": ["python", "main.py"],
    },
    "c": {
        "image": "codeforge-runner-cpp",
        "file": "main.c",
        "compile": ["gcc", "main.c", "-O2", "-o", "/workspace/codeforge-main"],
        "run": ["/workspace/codeforge-main"],
    },
    "cpp": {
        "image": "codeforge-runner-cpp",
        "file": "main.cpp",
        "compile": ["g++", "main.cpp", "-O2", "-std=c++20", "-o", "/workspace/codeforge-main"],
        "run": ["/workspace/codeforge-main"],
    },
    "java": {
        "image": "codeforge-runner-java",
        "file": "Main.java",
        "compile": ["javac", "-d", "/tmp", "Main.java"],
        "run": ["java", "-cp", "/tmp", "Main"],
    },
    "javascript": {
        "image": "codeforge-runner-node",
        "file": "main.js",
        "compile": None,
        "run": ["node", "main.js"],
    },
    "typescript": {
        "image": "codeforge-runner-node",
        "file": "main.ts",
        "compile": ["tsc", "main.ts", "--target", "ES2022", "--module", "commonjs", "--outDir", "/tmp"],
        "run": ["node", "/tmp/main.js"],
    },
    "go": {
        "image": "codeforge-runner-go",
        "file": "main.go",
        "compile": ["go", "build", "-o", "/workspace/codeforge-main", "main.go"],
        "run": ["/workspace/codeforge-main"],
    },
    "rust": {
        "image": "codeforge-runner-rust",
        "file": "main.rs",
        "compile": ["rustc", "-O", "main.rs", "-o", "/workspace/codeforge-main"],
        "run": ["/workspace/codeforge-main"],
    },
    "php": {
        "image": "codeforge-runner-php",
        "file": "main.php",
        "compile": None,
        "run": ["php", "main.php"],
    },
}
