"""
Blockchain-Based Traceability System
Immutable tracking of blood units from donor to transfusion
"""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid


class Block:
    """Individual block in the blockchain"""
    
    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2):
        """Proof of work - mine the block"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }


class BloodUnitBlockchain:
    """
    Blockchain for blood unit traceability
    
    Tracks entire lifecycle:
    - Donor → Collection → Testing → Storage → Hospital → Transfusion
    """
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.difficulty = 2
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            data={"type": "genesis", "message": "BloodFlow AI Blockchain Initialized"},
            previous_hash="0"
        )
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def create_blood_unit(self, donor_id: str, blood_type: str, 
                         collection_date: str, location: str) -> str:
        """
        Create a new blood unit and add to blockchain
        
        Returns:
            Unique blockchain ID for the blood unit
        """
        unit_id = f"UNIT-{uuid.uuid4().hex[:12].upper()}"
        
        transaction = {
            "type": "COLLECTION",
            "unit_id": unit_id,
            "blood_type": blood_type,
            "donor_id": donor_id,  # In production, this would be anonymized
            "collection_date": collection_date,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "status": "collected"
        }
        
        self.add_transaction(transaction)
        return unit_id
    
    def add_transaction(self, transaction: Dict):
        """Add a transaction to pending transactions"""
        self.pending_transactions.append(transaction)
    
    def mine_pending_transactions(self):
        """Mine all pending transactions into a new block"""
        if not self.pending_transactions:
            return None
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now().isoformat(),
            data={"transactions": self.pending_transactions},
            previous_hash=self.get_latest_block().hash
        )
        
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        return new_block
    
    def add_testing_record(self, unit_id: str, test_results: Dict):
        """Record blood testing results"""
        transaction = {
            "type": "TESTING",
            "unit_id": unit_id,
            "test_results": test_results,
            "tested_by": test_results.get("technician_id", "LAB-001"),
            "timestamp": datetime.now().isoformat(),
            "status": "tested" if test_results.get("passed", True) else "rejected"
        }
        self.add_transaction(transaction)
        self.mine_pending_transactions()
    
    def add_storage_record(self, unit_id: str, storage_location: str, 
                          temperature: float, expiry_date: str):
        """Record blood storage information"""
        transaction = {
            "type": "STORAGE",
            "unit_id": unit_id,
            "storage_location": storage_location,
            "temperature": temperature,
            "expiry_date": expiry_date,
            "timestamp": datetime.now().isoformat(),
            "status": "stored"
        }
        self.add_transaction(transaction)
        self.mine_pending_transactions()
    
    def add_transfer_record(self, unit_id: str, from_location: str, 
                           to_location: str, transported_by: str):
        """Record blood unit transfer between locations"""
        transaction = {
            "type": "TRANSFER",
            "unit_id": unit_id,
            "from_location": from_location,
            "to_location": to_location,
            "transported_by": transported_by,
            "timestamp": datetime.now().isoformat(),
            "status": "in_transit"
        }
        self.add_transaction(transaction)
        self.mine_pending_transactions()
    
    def add_transfusion_record(self, unit_id: str, hospital: str, 
                              patient_id: str, doctor_id: str):
        """Record blood transfusion (anonymized patient data)"""
        transaction = {
            "type": "TRANSFUSION",
            "unit_id": unit_id,
            "hospital": hospital,
            "patient_id_hash": hashlib.sha256(patient_id.encode()).hexdigest()[:16],  # Anonymized
            "doctor_id": doctor_id,
            "timestamp": datetime.now().isoformat(),
            "status": "transfused"
        }
        self.add_transaction(transaction)
        self.mine_pending_transactions()
    
    def get_unit_history(self, unit_id: str) -> List[Dict]:
        """
        Get complete history of a blood unit
        
        Returns all transactions related to this unit
        """
        history = []
        
        for block in self.chain:
            if "transactions" in block.data:
                for transaction in block.data["transactions"]:
                    if transaction.get("unit_id") == unit_id:
                        history.append({
                            "block_index": block.index,
                            "block_hash": block.hash,
                            "transaction": transaction
                        })
        
        return history
    
    def verify_unit_authenticity(self, unit_id: str) -> Dict:
        """
        Verify a blood unit exists and hasn't been tampered with
        
        Returns verification status and details
        """
        history = self.get_unit_history(unit_id)
        
        if not history:
            return {
                "verified": False,
                "message": "Unit ID not found in blockchain",
                "unit_id": unit_id
            }
        
        # Verify blockchain integrity
        is_valid = self.is_chain_valid()
        
        return {
            "verified": is_valid,
            "message": "Unit verified and authentic" if is_valid else "Blockchain compromised!",
            "unit_id": unit_id,
            "total_records": len(history),
            "current_status": history[-1]["transaction"]["status"] if history else "unknown",
            "blockchain_valid": is_valid
        }
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verify chain linkage
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_chain_info(self) -> Dict:
        """Get blockchain statistics"""
        total_transactions = sum(
            len(block.data.get("transactions", [])) 
            for block in self.chain
        )
        
        return {
            "total_blocks": len(self.chain),
            "total_transactions": total_transactions,
            "chain_valid": self.is_chain_valid(),
            "latest_block_hash": self.get_latest_block().hash,
            "difficulty": self.difficulty
        }
    
    def export_chain(self) -> List[Dict]:
        """Export entire blockchain for audit"""
        return [block.to_dict() for block in self.chain]
    
    def get_units_by_status(self, status: str) -> List[str]:
        """Get all blood units with a specific status"""
        units = set()
        
        for block in self.chain:
            if "transactions" in block.data:
                for transaction in block.data["transactions"]:
                    if transaction.get("status") == status:
                        units.add(transaction.get("unit_id"))
        
        return list(units)
    
    def get_audit_trail(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get audit trail for a date range
        For regulatory compliance
        """
        audit_records = []
        
        for block in self.chain:
            block_time = block.timestamp
            if start_date <= block_time <= end_date:
                if "transactions" in block.data:
                    for transaction in block.data["transactions"]:
                        audit_records.append({
                            "block": block.index,
                            "timestamp": transaction.get("timestamp"),
                            "type": transaction.get("type"),
                            "unit_id": transaction.get("unit_id"),
                            "status": transaction.get("status"),
                            "block_hash": block.hash
                        })
        
        return audit_records


# Global blockchain instance
blood_blockchain = BloodUnitBlockchain()
