import Administrator


def main():
    admin = Administrator.AdminUI()
    if admin.auth():
        admin.menu()
        exit()
    else:
        print("Exiting app due to bad authetication.")
        exit()

if __name__ == "__main__":
        main()
