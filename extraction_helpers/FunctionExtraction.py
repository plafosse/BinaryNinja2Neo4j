from binaryninja import *
import xxhash

################################################################################################################
#                                       MLIL FUNCTION                                                          #
################################################################################################################

"""
UUID - _uuid of the node
HASH - xxhash of the full file assembly, NOT MLIL
"""


class Neo4jFunction:

    def __init__(self, mlil_func, uuid):
        self.UUID = uuid
        self.func = mlil_func
        self.source_function = self.func.source_function
        self.bv = self.source_function.view
        self.HASH = self.func_hash()

    def func_hash(self):
        function_hash = xxhash.xxh32()
        br = BinaryReader(self.bv)

        for basic_block in self.source_function:
            br.seek(basic_block.start)
            bb_txt = br.read(basic_block.length)
            function_hash.update(bb_txt)

        return function_hash.intdigest()

    def to_dict(self):
        node_dict = {
            'UUID': self.UUID,
            'HASH': self.HASH,
        }
        relationship_dict = {
            'parent_function': self.func.source_function.name,
        }
        metadata_dict = {
            'NodeLabel': 'Function',
            'RelationshipLabel': 'bvToFunction'
        }
        obj_dict = {
            'NodeParams': node_dict,
            'RelationshipParams': relationship_dict,
            'Metadata': metadata_dict,
        }

        return obj_dict
