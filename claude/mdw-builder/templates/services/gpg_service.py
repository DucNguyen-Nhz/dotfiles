import os
import gnupg
from typing import Optional, List, Tuple


def _ensure_dir_for_file(path: str) -> None:
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def gpg_encrypt_file(
        input_filepath: str,
        output_filepath: Optional[str] = None,
        recipients: Optional[list] = None,
        passphrase: Optional[str] = None,
        use_symmetric: bool = False,
        gnupg_home: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Mã hóa file bằng GPG.
    - Nếu use_symmetric=True sẽ dùng mã hóa đối xứng (passphrase bắt buộc).
    - Nếu use_symmetric=False sẽ dùng mã hóa bất đối xứng, cần recipients (list of key ids / emails).
    - Trả về (success, message_or_output_path)
    """

    if not os.path.exists(input_filepath):
        return False, f"Input file not found: {input_filepath}"

    if output_filepath is None:
        if use_symmetric:
            output_filepath = input_filepath + ".gpg"
        else:
            output_filepath = input_filepath + ".gpg"

    _ensure_dir_for_file(output_filepath)

    gpg = gnupg.GPG(gnupghome=gnupg_home) if gnupg_home else gnupg.GPG()

    with open(input_filepath, "rb") as f:
        if use_symmetric:
            if not passphrase:
                return False, "Passphrase is required for symmetric encryption"
            result = gpg.encrypt_file(
                f,
                recipients=None,
                symmetric=True,
                passphrase=passphrase,
                output=output_filepath,
            )
        else:
            if not recipients or not isinstance(recipients, (list, tuple)) or len(recipients) == 0:
                return False, "Recipients (list of key IDs/emails) required for asymmetric encryption"
            result = gpg.encrypt_file(
                f,
                recipients=recipients,
                symmetric=False,
                output=output_filepath,
            )

    if not result:
        # result.status may contain reason text; result.stderr as well
        return False, f"Encryption failed: status={result.status} stderr={getattr(result, 'stderr', '')}"
    return True, output_filepath


def gpg_decrypt_file(
        input_filepath: str,
        output_filepath: Optional[str] = None,
        passphrase: Optional[str] = None,
        gnupg_home: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Giải mã file GPG.
    - Nếu private key được khóa bằng passphrase, truyền passphrase.
    - Trả về (success, message_or_output_path)
    """
    if not os.path.exists(input_filepath):
        return False, f"Input file not found: {input_filepath}"

    if output_filepath is None:
        # mặc định xoá extension .gpg hoặc .asc; nếu không có, thêm .dec
        base = input_filepath
        if base.endswith(".gpg") or base.endswith(".asc") or base.endswith(".pgp"):
            output_filepath = base.rsplit(".", 1)[0]
        else:
            output_filepath = base + ".dec"

    _ensure_dir_for_file(output_filepath)

    gpg = gnupg.GPG(gnupghome=gnupg_home) if gnupg_home else gnupg.GPG()

    with open(input_filepath, "rb") as f:
        try:
            # decrypt_file trả về object có .ok, .status, .stderr
            if passphrase:
                result = gpg.decrypt_file(f, passphrase=passphrase, output=output_filepath)
            else:
                result = gpg.decrypt_file(f, output=output_filepath)
        except Exception as e:
            return False, f"Exception during decryption: {str(e)}"

    if not result.ok:
        # nếu fail, xoá file output (nếu có) để tránh dữ liệu rác
        try:
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
        except OSError:
            pass
        return False, f"Decryption failed: status={getattr(result, 'status', '')} stderr={getattr(result, 'stderr', '')}"

    return True, output_filepath


class GPGService:
    def __init__(self, gnupg_home: Optional[str] = None):
        self.gnupg_home = gnupg_home

    def encrypt(
            self,
            input_file: str,
            output_file: Optional[str] = None,
            recipients: Optional[List[str]] = None,
            passphrase: Optional[str] = None,
            use_symmetric: bool = False,
    ) -> Tuple[bool, str]:
        """
        Service: mã hóa file
        """
        return gpg_encrypt_file(
            input_filepath=input_file,
            output_filepath=output_file,
            recipients=recipients,
            passphrase=passphrase,
            use_symmetric=use_symmetric,
            gnupg_home=self.gnupg_home,
        )

    def decrypt(
            self,
            input_file: str,
            output_file: Optional[str] = None,
            passphrase: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Service: giải mã file
        """
        return gpg_decrypt_file(
            input_filepath=input_file,
            output_filepath=output_file,
            passphrase=passphrase,
            gnupg_home=self.gnupg_home,
        )
