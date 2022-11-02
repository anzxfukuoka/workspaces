# This is a Python script starts up a set apps are
# used in the same time with specified params.
import json
import subprocess
import click
from os import path
from pathlib import Path

WORKSPACES_FILE = path.join(Path.home(), "workspaces.json")
#print(WORKSPACES_FILE)


@click.group()
def main():
    pass


def load_workspaces(file_path):
    backup_file = file_path + ".bak"

    # trying to load workspaces file
    if not path.exists(file_path):
        print("no workspaces file")
        user_workspaces = {}
        return user_workspaces

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            user_workspaces = json.load(f)
        except json.decoder.JSONDecodeError as e:
            user_workspaces = None

    if not user_workspaces:
        # if an error occurred
        print("workspaces file parsing failed")

        if path.exists(backup_file):
            print("trying load backup file...")
            with open(backup_file, "r", encoding="utf-8") as f:
                try:
                    user_workspaces = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    print("backup file parsing failed")
                    user_workspaces = {}
        else:
            user_workspaces = {}
    else:
        # updating backup file
        with open(backup_file, "w+", encoding="utf-8") as f:
            json.dump(user_workspaces, f)

    return user_workspaces


def save_workspaces(file_path, user_workspaces):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_workspaces, f)


@main.command(help="list workspaces")
@click.option("--workspace", "-w", default=None, help="workspace name")
def show(workspace):
    user_workspaces = load_workspaces(WORKSPACES_FILE)

    if workspace:
        if workspace in user_workspaces:
            apps_list = user_workspaces[workspace]["apps"]
            print("\n".join(["{}\t{}".format(i, a) for i, a in enumerate(apps_list)]))
        else:
            print("invalid workspace name")
    else:
        if user_workspaces is {}:
            return
        print("workspaces list:", end="\n\t")
        print("\n\t".join(user_workspaces.keys()))


@main.command(help="creates new workspace")
@click.option("--name", "-n", required=True, help="workspace name")
@click.option("--desc", "-d", default="", help="description")
def create(name, desc):
    user_workspaces = load_workspaces(WORKSPACES_FILE)

    #print(user_workspaces)

    if name not in user_workspaces:
        user_workspaces.update({name: {
            "name": name,
            "description": desc,
            "apps": []}})
    else:
        print("workspace with name {} already exists".format(name))

    save_workspaces(WORKSPACES_FILE, user_workspaces)

    #print(user_workspaces)

    # print("workspace {} created".format(name))


@main.command(help="add app to workspace")
@click.option("--workspace", "-w", required=True, help="workspace name")
@click.option("--executable_path", "-e", required=True, help="path to executable")
@click.option("--args", "-a", default="", help="args")
def add(workspace, executable_path, args):
    user_workspaces = load_workspaces(WORKSPACES_FILE)

    if workspace not in user_workspaces:
        print("invalid workspace name")
        return

    user_workspaces[workspace]["apps"].append({
        "executable_path": executable_path,
        "args": args})

    save_workspaces(WORKSPACES_FILE, user_workspaces)


@main.command(help="remove app from workspace")
@click.option("--workspace", "-w", required=True, help="workspace name")
@click.option("--index", "-i", required=True, help="index", type=int)
def remove(workspace, index):
    user_workspaces = load_workspaces(WORKSPACES_FILE)

    if workspace not in user_workspaces:
        print("invalid workspace name")
        return

    length = len(user_workspaces[workspace]["apps"])

    if length == 0:
        print("workspaces {} apps list is empty".format(workspace))
        return

    try:
        user_workspaces[workspace]["apps"].pop(index)
        save_workspaces(WORKSPACES_FILE, user_workspaces)
    except IndexError as e:
        print("index ({}) out of range (0, {})".format(index, length))


@main.command(help="start workspace")
@click.option("--workspace", "-w", required=True, help="workspace name")
def start(workspace):
    user_workspaces = load_workspaces(WORKSPACES_FILE)

    if workspace not in user_workspaces:
        print("invalid workspace name")
        return

    apps_list = user_workspaces[workspace]["apps"]

    for app in apps_list:
        exec_path = app["executable_path"]
        args = app["args"]
        print(exec_path, args)
        a = subprocess.run([exec_path] + args.split(" "))
        print(a)


if __name__ == '__main__':
    main()
