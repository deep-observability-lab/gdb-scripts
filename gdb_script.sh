#!/bin/bash

REQUIREMENTS_FILE="requirements.txt"
VENV_DIR="env"
if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
    echo "requirements.txt not found! Exiting..."
    exit 1
fi

echo "Creating a Python virtual environment..."
python3 -m venv "$VENV_DIR"
echo "Activating the virtual environment..."
source "$VENV_DIR/bin/activate"  # For Linux/macOS

echo "Installing dependencies from requirements.txt..."
pip install -r "$REQUIREMENTS_FILE"


deactive_env() {
    echo "Deactivating the virtual environment..."
    deactivate
    rm -rf "$VENV_DIR"
}

trap deactive_env EXIT


input_args=("$@")

workspace=""
source_code=""
filtered_args=()
gdb_mode=""
binary=""
coredump=""
docker_mode=""
skip_next=false
team_choice=""
architecture=""
for ((i = 0; i < ${#input_args[@]}; i++)); do
    if [[ "$skip_next" == true ]]; then
        skip_next=false
        continue
    fi
    shopt -s nocasematch
    case "${input_args[i]}" in
        -w)
            if [[ -n "${input_args[i+1]}" && "${input_args[i+1]}" != -* ]]; then
                workspace="${input_args[i+1]}"
            fi
            filtered_args+=("${input_args[i]}" "${input_args[i+1]}")
            skip_next=true  
            ;;
        -p)
            if [[ -n "${input_args[i+1]}" && "${input_args[i+1]}" != -* ]]; then
                binary="${input_args[i+1]}"
            fi
            filtered_args+=("${input_args[i]}" "${input_args[i+1]}")
            skip_next=true  
            ;;    
        -s)
            if [[ -n "${input_args[i+1]}" && "${input_args[i+1]}" != -* ]]; then
                source_code="${input_args[i+1]}"
            fi
            filtered_args+=("${input_args[i]}" "${input_args[i+1]}")
            skip_next=true  
            ;;
        -c)
            if [[ -n "${input_args[i+1]}" && "${input_args[i+1]}" != -* ]]; then
                coredump="${input_args[i+1]}"
                input_args[i+1]=$(basename "$coredump")
            fi
            filtered_args+=("${input_args[i]}" "${input_args[i+1]}")
            skip_next=true  
            ;;
        --docker)
            if [[ "${input_args[i]}" == --* ]]; then
                docker_mode="yes"    
            fi
            skip_next=false 
            ;;
        gdb_coredump | gdb_remote)
            gdb_mode="${input_args[i]}"
            filtered_args+=("${input_args[i]}")
            ;;
        *)
            filtered_args+=("${input_args[i]}")
            ;;
    esac
    shopt -u nocasematch
done


filename=""

if [[ -n "$coredump" && -f "$coredump" ]]; then
    filename=$(basename "$coredump")

    cp "$coredump" "$workspace/$filename"
    #echo "File '$filename' copied to $workspace."
else
    echo "Error: '$coredump' is not a valid file path or does not exist."
    exit 1
fi

if [[ "$docker_mode" == "yes" ]]; then
    echo "Running in Docker mode..."
    # docker pull 33zahra/gdb-scripts:latest
    # docker tag 33zahra/gdb-scripts:latest gdb-scripts:latest
    
    if [[ "$gdb_mode" == "gdb_coredump" ]]; then
        echo 
        if [[ -n "$source_code" ]]; then
            docker run -v "$workspace":/work -v "$source_code":/src -it gdb-scripts "${filtered_args[@]}"   #gdb_coredump
        else
            docker run -v "$workspace":/work -it gdb-scripts "${filtered_args[@]}"   #gdb_coredump 
        fi
    elif [[ "$gdb_mode" == "gdb_remote" ]]; then
        if [[ -n "$source_code" ]]; then
            docker run -v "$workspace":/work -v "$source_code":/src -it gdb-scripts "${filtered_args[@]}" #gdb_remote
        else
            docker run -v "$workspace":/work -it gdb-scripts "${filtered_args[@]}" #gdb_remote
        fi
    else
        echo "Error: No valid gdb mode found. enter gdb_coredump or gdb_remote"
        exit 1
    fi
else
    echo "Running in normal mode..."
    if [[ "$gdb_mode" == "gdb_coredump" ]]; then
        ./entrypoint.sh "${filtered_args[@]}"
    elif [[ "$gdb_mode" == "gdb_remote" ]]; then
        ./entrypoint.sh "${filtered_args[@]}"
    else
        exit 1
    fi
fi
