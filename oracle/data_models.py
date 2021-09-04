from dataclasses import dataclass


@dataclass
class Transaction:
    Account: str
    Amount: str
    Destination: str
    Fee: str
    Flags: int
    LastLedgerSequence: int
    Sequence: int
    SigningPubKey: str
    TransactionType: str
    TxnSignature: str
    date: int
    hash: str
    inLedger: int
    ledger_index: int

