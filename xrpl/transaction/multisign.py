"""Multisign transaction methods with XRPL transactions."""
from typing import List

from xrpl.models.transactions.transaction import Signer, Transaction


def multisign(transaction: Transaction, tx_list: List[Transaction]) -> Transaction:
    """
    Takes several transactions with Signer fields and creates a
    single transaction with all Signers that then gets signed and returned.

    Args:
        transaction: the transaction to be multisigned.
        tx_list: a list of signed transactions to combine into a single multisigned
            transaction.

    Returns:
        The multisigned transaction.
    """
    tx_xrpl_list = [tx.to_xrpl() for tx in tx_list]

    decoded_tx_signers = [tx_xrpl["Signers"][0]["Signer"] for tx_xrpl in tx_xrpl_list]

    tx_dict = transaction.to_dict()
    tx_dict["signers"] = [
        Signer(
            account=decoded_tx_signer["Account"],
            txn_signature=decoded_tx_signer["TxnSignature"],
            signing_pub_key=decoded_tx_signer["SigningPubKey"],
        )
        for decoded_tx_signer in decoded_tx_signers
    ]

    return Transaction.from_dict(tx_dict)
