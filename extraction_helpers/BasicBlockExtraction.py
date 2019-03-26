from binaryninja import *
import xxhash

################################################################################################################
#                                       MLIL BASIC BLOCK                                                       #
################################################################################################################

"""
HASH - xxhash of the basic block, created by digesting all tokens from all instructions within the basic block
"""


class Neo4jBasicBlock:

    def __init__(self, bb, uuid):
        self.UUID = uuid
        self.bb = bb
        self.HASH = self.bb_hash()

    def bb_hash(self):
        mlil_bb_hash = xxhash.xxh32()

        for disasm_text in self.bb.disassembly_text:
            if 'sub_' not in str(disasm_text):
                mlil_bb_hash.update(str(disasm_text))

        return mlil_bb_hash.intdigest()

    def to_dict(self):
        node_dict = {
            'UUID': self.UUID,
            'HASH': self.HASH,
        }
        relationship_dict = {
            'parent_function': self.bb.function.name,
            'bb_offset': self.bb.start,
        }
        metadata_dict = {
            'NodeLabel': 'BasicBlock',
            'RelationshipLabel': 'FuncToBasicBlock'
        }
        obj_dict = {
            'NodeParams': node_dict,
            'RelationshipParams': relationship_dict,
            'Metadata': metadata_dict,
        }
        return obj_dict
