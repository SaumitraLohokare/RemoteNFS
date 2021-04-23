def sanitizeFilePath(path: str) -> str:
    return path.replace('\\', '/')

def setupEnv(params: dict):
    with open('resources/.env', 'w') as f:
        lines = [
            f"PARENT_FOLDER={params['PARENT_FOLDER']}"
        ]
        f.writelines(lines)
        f.flush()