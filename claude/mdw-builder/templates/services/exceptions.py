class FileNotImportedSFTP(Exception):

    def __init__(self, filename="") -> None:

        message = f"Import file {filename} not found on sFTP server"
        super().__init__(message)

        self.filename = filename
