#!/bin/bash
# ultimate_gitignore.sh
# Auto-update .gitignore for multi-project + submodules

OUTPUT_FILE=".gitignore"
TEMP_FILE=".gitignore.tmp"

> "$TEMP_FILE"

append_rule() {
  local rule="$1"
  grep -qxF "$rule" "$TEMP_FILE" || echo "$rule" >> "$TEMP_FILE"
}

# -------------------------
# System / Editor / Logs
# -------------------------
SYSTEM_RULES=(
".DS_Store"
"Thumbs.db"
"*.log"
"*.tmp"
"*.bak"
"*.old"
"*.orig"
"*.swp"
".idea/"
".vscode/"
"*.iml"
"*.classpath"
"*.project"
"*.xcuserstate"
)
for rule in "${SYSTEM_RULES[@]}"; do append_rule "$rule"; done

# -------------------------
# Detect project types recursively (root + submodules)
# -------------------------
PROJECT_TYPES=()
PROJECT_PATHS=$(find . -name "package.json" -o -name "*.py" -o -name "build.gradle" -o -name "*.java" -o -name "*.xcodeproj" -o -name "Podfile")

for path in $PROJECT_PATHS; do
  case "$path" in
    *.py) PROJECT_TYPES+=("python") ;;
    package.json) PROJECT_TYPES+=("node") ;;
    build.gradle|*.java) PROJECT_TYPES+=("java") ;;
    *.xcodeproj|Podfile) PROJECT_TYPES+=("ios") ;;
  esac
done

# remove duplicates
PROJECT_TYPES=($(echo "${PROJECT_TYPES[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

# -------------------------
# Node.js
# -------------------------
if [[ " ${PROJECT_TYPES[@]} " =~ " node " ]]; then
  NODE_RULES=("node_modules/" "dist/" ".env" "package-lock.json" "yarn-error.log*" "yarn-debug.log*")
  for rule in "${NODE_RULES[@]}"; do append_rule "$rule"; done
fi

# -------------------------
# Python
# -------------------------
if [[ " ${PROJECT_TYPES[@]} " =~ " python " ]]; then
  PYTHON_RULES=("__pycache__/" "*.py[cod]" "*\$py.class" "venv/" "env/" ".ipynb_checkpoints")
  for rule in "${PYTHON_RULES[@]}"; do append_rule "$rule"; done
fi

# -------------------------
# Java / Android
# -------------------------
if [[ " ${PROJECT_TYPES[@]} " =~ " java " ]]; then
  JAVA_RULES=("*.class" "/build/" "/target/" "/captures/" "/output/" ".gradle/" "local.properties" "*.apk" "*.keystore")
  for rule in "${JAVA_RULES[@]}"; do append_rule "$rule"; done
fi

# -------------------------
# iOS / Swift
# -------------------------
if [[ " ${PROJECT_TYPES[@]} " =~ " ios " ]]; then
  IOS_RULES=("build/" "DerivedData/" "*.xcworkspace" "*.moved-aside" "Pods/" "*.xcodeproj/project.xcworkspace/")
  for rule in "${IOS_RULES[@]}"; do append_rule "$rule"; done
fi

# -------------------------
# Optional / Backup / OS
# -------------------------
OPTIONAL_RULES=("*.swp" "*.swo" "*.bak" "*.old" "*.orig" "*.tmp")
for rule in "${OPTIONAL_RULES[@]}"; do append_rule "$rule"; done

# -------------------------
# Gabungkan dengan rules lama
# -------------------------
if [ -f "$OUTPUT_FILE" ]; then
  cat "$OUTPUT_FILE" >> "$TEMP_FILE"
fi

# hapus duplikat & update .gitignore
sort -u "$TEMP_FILE" > "$OUTPUT_FILE"
rm "$TEMP_FILE"

echo ".gitignore updated for multi-project and submodules!"