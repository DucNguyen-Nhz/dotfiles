import paramiko
import logging
from django.conf import settings

logger = logging.getLogger("info_logger")

class SFTPService:
    _instance = None
    _sftp = None

    host = settings.SFTP_HOST
    port = settings.SFTP_PORT
    username = settings.SFTP_USER
    password = settings.SFTP_PASS

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._transport = None
            cls._instance._sftp = None
        return cls._instance

    def _ensure_connected(self):
        if self._transport is None or not self._transport.is_active():
            self._transport = paramiko.Transport((self.host, self.port))
            self._transport.connect(username=self.username, password=self.password)
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)

    def disconnect(self):
        if self._sftp:
            self._sftp.close()
            self._sftp = None

        if self._transport:
            self._transport.close()
            self._transport = None

    def download_file(self, remote_path: str, local_path: str):
        self._ensure_connected()
        try:
            if self._sftp is None:
                raise ValueError("sftp is null")

            self._sftp.get(remote_path, local_path)
        except Exception as e:
            logger.error("An error occurred while downloading SFTP file", exc_info=e)
            raise

    def rename_file(self, remote_path: str, new_name: str):
        self._ensure_connected()
        try:
            if self._sftp is None:
                raise ValueError("sftp is null")

            remote_dir = remote_path.rsplit("/", 1)[0]
            new_remote_path = f"{remote_dir}/{new_name}"
            self._sftp.rename(remote_path, new_remote_path)
        except Exception as e:
            logger.error("An error occurred while renaming SFTP file", exc_info=e)
            raise

    def upload_file(self, remote_path: str, local_path: str):
        self._ensure_connected()
        try:
            if self._sftp is None:
                raise ValueError("sftp is null")

            self._sftp.put(local_path, remote_path)
        except Exception as e:
            logger.error("An error occurred while uploading SFTP file", exc_info=e)
            raise

    def remote_file_exist(self, remote_path: str) -> bool:
        self._ensure_connected()
        try:
            if self._sftp is None:
                raise ValueError("sftp is null")

            self._sftp.stat(remote_path)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error("An error occurred while checking SFTP file existence", exc_info=e)
            raise

    def remove_file(self, remote_path: str):
        self._ensure_connected()
        try:
            if self._sftp is None:
                raise ValueError("sftp is null")

            self._sftp.remove(remote_path)
        except Exception as e:
            logger.error("An error occurred while removing SFTP file", exc_info=e)
            raise


class SFTPService:

    def __init__(self, host, port=22, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def _connect(self):
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return transport, sftp

    def download_file(self, remote_path: str, local_path: str):
        transport, sftp = self._connect()
        try:
            sftp.get(remote_path, local_path)
        except Exception as e:
            logger.error("An error occurred while downloading SFTP file", exc_info=e)
            raise e
        finally:
            sftp.close()
            transport.close()

    def rename_file(self, remote_path: str, new_name: str):
        """
        Đổi tên file từ remote_path sang cùng thư mục nhưng với tên new_name.
        """
        transport, sftp = self._connect()
        try:
            remote_dir = remote_path.rsplit("/", 1)[0]
            new_remote_path = f"{remote_dir}/{new_name}"
            sftp.rename(remote_path, new_remote_path)
        except Exception as e:
            logger.error("An error occurred while renaming SFTP file", exc_info=e)
            raise e
        finally:
            sftp.close()
            transport.close()

    def upload_file(self, remote_path: str, local_path: str):
        transport, sftp = self._connect()
        try:
            sftp.put(local_path, remote_path)
        except Exception as e:
            logger.error("An error occurred while uploading SFTP file", exc_info=e)
            raise e
        finally:
            sftp.close()
            transport.close()

    def remote_file_exist(self, remote_path: str) -> bool:
        transport, sftp = self._connect()
        try:
            sftp.stat(remote_path)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error("An error occurred while checking SFTP file existence", exc_info=e)
            raise e
        finally:
            sftp.close()
            transport.close()
            
    def remove_file(self, remote_path: str) -> bool:
        transport, sftp = self._connect()
        
        try:
            sftp.remove(remote_path)
        except Exception as e:
            logger.error("An error occurred while removing SFTP file", exc_info=e)
            raise
        finally:
            sftp.close()
            transport.close()
