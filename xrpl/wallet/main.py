"""The information needed to control an XRPL account."""

from __future__ import annotations

from typing import Optional, Type

from xrpl.constants import CryptoAlgorithm
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.core.keypairs import derive_classic_address, derive_keypair, generate_seed
from xrpl.utils.ensure_classic_address import ensure_classic_address


class Wallet:
    """
    The cryptographic keys needed to control an XRP Ledger account. See
    `Cryptographic Keys <https://xrpl.org/cryptographic-keys.html>`_ for
    details.
    """

    @property
    def address(self: Wallet) -> str:
        """
        Alias for wallet.classic_address.

        Returns:
            The address that publicly identifies this wallet, as a base58 string.
        """
        return self.classic_address

    def __init__(
        self: Wallet,
        public_key: str,
        private_key: str,
        *,
        master_address: Optional[str] = None,
        seed: Optional[str] = None,
    ) -> None:
        """
        Generate a new Wallet.

        Args:
            public_key: The public key for the account.
            private_key: The private key used for signing transactions for the account.
            master_address: Include if a Wallet uses a Regular Key Pair. It must be
                the master address of the account. The default is `None`.
            seed: The seed used to derive the account keys. The default is `None`.
        """
        self.public_key = public_key
        """
        The public key that is used to identify this wallet's signatures, as
        a hexadecimal string.
        """

        self.private_key = private_key
        """
        The private key that is used to create signatures, as a hexadecimal
        string. MUST be kept secret!
        """

        self.classic_address = (
            ensure_classic_address(master_address)
            if master_address is not None
            else derive_classic_address(self.public_key)
        )
        """The address that publicly identifies this wallet, as a base58 string."""

        self.seed = seed
        """
        The core value that is used to derive all other information about
        this wallet. MUST be kept secret!
        """

    @classmethod
    def generate(
        cls: Type[Wallet], algorithm: CryptoAlgorithm = CryptoAlgorithm.ED25519
    ) -> Wallet:
        """
        Generates a new seed and Wallet.

        Args:
            algorithm: The digital signature algorithm to generate an address for.
                The default is Ed25519.

        Returns:
            The wallet that is generated from the given seed.
        """
        seed = generate_seed(algorithm=algorithm)
        return Wallet.from_seed(seed, algorithm=algorithm)

    @classmethod
    def from_seed(
        cls: Type[Wallet],
        seed: str,
        *,
        master_address: Optional[str] = None,
        algorithm: CryptoAlgorithm = CryptoAlgorithm.ED25519,
    ) -> Wallet:
        """
        Generates a new Wallet from seed (secret).

        Args:
            seed: The seed (secret) used to derive the account keys.
            master_address: Include if a Wallet uses a Regular Key Pair. It must be
                the master address of the account. The default is `None`.
            algorithm: The digital signature algorithm to generate an address for.
                The default is ED25519.

        Returns:
            The wallet that is generated from the given secret.
        """
        public_key, private_key = derive_keypair(seed, algorithm=algorithm)
        return cls(public_key, private_key, master_address=master_address, seed=seed)

    from_secret = from_seed

    @classmethod
    def from_entropy(
        cls: Type[Wallet],
        entropy: str,
        *,
        master_address: Optional[str] = None,
        algorithm: CryptoAlgorithm = CryptoAlgorithm.ED25519,
    ) -> Wallet:
        """
        Generates a new Wallet from entropy (array of random numbers).

        Args:
            entropy: A string of random numbers to generate a seed used to derive
                a wallet.
            master_address: Include if a Wallet uses a Regular Key Pair. It must be
                the master address of the account. The default is `None`.
            algorithm: The digital signature algorithm to generate an address for.
                The default is ED25519.

        Returns:
            The wallet that is generated from the given entropy.
        """
        seed = generate_seed(entropy, algorithm)
        return Wallet.from_seed(
            seed, master_address=master_address, algorithm=algorithm
        )

    def get_xaddress(
        self: Wallet, *, tag: Optional[int] = None, is_test: bool = False
    ) -> str:
        """
        Returns the X-Address of the Wallet's account.

        Args:
            tag: The destination tag of the address. Defaults to `None`.
            is_test: Whether the address corresponds to an address on the test network.
                Defaults to `False`.

        Returns:
            The X-Address of the Wallet's account.
        """
        return classic_address_to_xaddress(self.classic_address, tag, is_test)

    def __str__(self: Wallet) -> str:
        """
        Returns a string representation of a Wallet.

        Returns:
            A string representation of a Wallet.
        """
        return "\n".join(
            [
                f"public_key: {self.public_key}",
                "private_key: -HIDDEN-",
                f"classic_address: {self.classic_address}",
            ]
        )
