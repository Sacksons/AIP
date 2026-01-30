"""Blockchain notarization models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class BlockchainRecord(Base):
    """Blockchain notarization record for verification proofs."""

    __tablename__ = "blockchain_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    project_id = Column(Integer, ForeignKey("aip_projects.id", ondelete="CASCADE"), nullable=False)

    # Record type
    record_type = Column(String(100), nullable=False)  # verification, document, milestone
    reference_id = Column(String(100))  # verification_request_id, document_id, etc.

    # Blockchain details
    chain_id = Column(Integer, nullable=False)  # 137=Polygon, 42161=Arbitrum, etc.
    chain_name = Column(String(50), nullable=False)  # polygon, arbitrum, base
    contract_address = Column(String(42), nullable=False)
    tx_hash = Column(String(66), unique=True, nullable=False)
    block_number = Column(Integer)
    block_timestamp = Column(DateTime)

    # Proof data
    data_hash = Column(String(66), nullable=False)  # keccak256 of the data
    ipfs_cid = Column(String(100))  # Optional IPFS content ID
    metadata_json = Column(JSON)  # Additional structured metadata

    # Status
    status = Column(String(50), default="pending", nullable=False)  # pending, confirmed, failed
    confirmations = Column(Integer, default=0)
    gas_used = Column(Integer)
    gas_price_gwei = Column(Integer)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime)

    # Relationships
    project = relationship("Project", back_populates="blockchain_records")

    def __repr__(self):
        return f"<BlockchainRecord {self.record_type} tx={self.tx_hash[:10]}...>"

    @property
    def explorer_url(self) -> str:
        """Get block explorer URL for this transaction."""
        explorers = {
            137: "https://polygonscan.com/tx/",
            42161: "https://arbiscan.io/tx/",
            8453: "https://basescan.org/tx/",
            1: "https://etherscan.io/tx/",
        }
        base_url = explorers.get(self.chain_id, "")
        return f"{base_url}{self.tx_hash}" if base_url else ""
