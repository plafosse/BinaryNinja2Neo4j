from binaryninja import *
import xxhash

################################################################################################################
#                                       MLIL Instruction                                                       #
################################################################################################################

class Neo4jInstruction:

    def __init__(self, instr, uuid):
        self.UUID = uuid
        self.instr = instr
        self.HASH = self.instr_hash()

    def instr_hash(self):
        instruction_hash = xxhash.xxh32()
        instruction_hash.update(str(self.instr.tokens).strip('[').strip(']').replace("'", '').replace(",", ''))

        return instruction_hash.intdigest()

    def to_dict(self):
        node_dict = {
            'UUID': self.UUID,
            'HASH': self.HASH,

        }
        relationship_dict = {
            'parent_function': self.instr.function.source_function.name,
            'index': self.instr.instr_index,
        }
        metadata_dict = {
            'NodeLabel': 'Instruction',
            'RelationshipLabel': 'Instruction'
        }
        obj_dict = {
            'NodeParams': node_dict,
            'RelationshipParams': relationship_dict,
            'Metadata': metadata_dict,
        }

        return obj_dict
