"""
this module contains all the procedures for extracting data from a binary ninja binary view.
"""

from . import data_structures
from . import database
from .extraction_helpers import BinaryViewExtraction, FunctionExtraction, BasicBlockExtraction, InstructionExtraction


class BinjaGraph:

    def __init__(self, driver, uuid_obj, bv):
        self._driver = driver
        self._uuid_obj = uuid_obj
        self.bv = bv

    def bv_extract(self):
        """
        populate the graph with relevant info from the bv itself
        :return: success: (BOOLEAN)
        """
        bv_object = BinaryViewExtraction.Neo4jBinaryView(self.bv, self._uuid_obj.get_uuid())
        bv_actual_uuid = self.serialize_node_obj(bv_object.to_dict(), bv_object.parent_uuid)
        if bv_actual_uuid:
            for func in self.bv:
                self.func_extract(func, bv_actual_uuid)

    def func_extract(self, func, parent_uuid):
        func_object = FunctionExtraction.Neo4jFunction(func.mlil, self._uuid_obj.get_uuid())
        func_actual_uuid = self.serialize_node_obj(func_object.to_dict(), parent_uuid)
        if func_actual_uuid:
            for basic_block in func.mlil:
                self.bb_extract(basic_block, func_actual_uuid)

    def bb_extract(self, basic_block, parent_uuid):
        bb_object = BasicBlockExtraction.Neo4jBasicBlock(basic_block, self._uuid_obj.get_uuid())
        bb_actual_uuid = self.serialize_node_obj(bb_object.to_dict(), parent_uuid)
        if bb_actual_uuid:
            parent_uuid = bb_actual_uuid
            for instruction in basic_block:
                parent_uuid = self.instruction_extract(instruction, parent_uuid)

    def instruction_extract(self, instruction, parent_uuid):
        instr_object = InstructionExtraction.Neo4jInstruction(instruction, self._uuid_obj.get_uuid())
        instr_actual_uuid = self.serialize_node_obj(instr_object.to_dict(), parent_uuid)
        for index in range(len(instruction.operands)):
            for op_description in instruction.ILOperations[instruction.operation]:
                op_description_type = op_description[1]
                op_description_name = op_description[0]
                if op_description_type == 'expr':
                    continue
                if op_description_type == 'var':
                    continue
                if op_description_type == 'expr_list':
                    continue
                if op_description_type == 'var_list':
                    continue
                if op_description_type == 'int':
                    continue
                if op_description_type == 'int_list':
                    continue
                if op_description_type == 'float':
                    continue
                if op_description_type == 'var_ssa':
                    continue
                if op_description_type == 'var_ssa_dest_and_src':
                    continue
                if op_description_type == 'var_ssa_list':
                    continue
                if op_description_type == 'intrinsic':
                    continue
        return instr_actual_uuid

    def serialize_node_obj(self, obj, parent_uuid):
        """
        receives an object and populates the DB with it.
        object is a nested dictionary that complies to a neo4j object
        :param obj: the object to serialize into the DB
        :param parent_uuid: (INT) the UUID of the parent node to the obj node
        :return: (INT) UUID of the current created node
        """
        with self._driver.session() as session:
            with session.begin_transaction() as tx:
                new_uuid = 0

                result = tx.run("MATCH (n {HASH:$hash}) "
                                "RETURN n.UUID",
                                hash=obj['NodeParams']['HASH'])
                if not (result.peek()):
                    # if results has no records then no node matched, need to create a new node
                    new_node = tx.run("CALL apoc.create.node([$NodeLabel], $params) YIELD node",
                                      params=obj['NodeParams'], NodeLabel=obj['Metadata']['NodeLabel'])
                    if new_node.peek():
                        # UUID of the newly created node
                        new_uuid = new_node.peek()['node']['UUID']
                else:
                    # no new node was created, return the UUID of the existing node
                    new_uuid = result.peek()['n.UUID']

                #create the new relationship
                tx.run("MATCH (p {UUID: $parent_uuid})"
                       "MATCH (n {UUID: $uuid})"
                       "MERGE (p)-[r:Includes {parent_function: $pf}]->(n)"
                       "ON CREATE SET r = $params",
                       uuid=obj['NodeParams']['UUID'], parent_uuid=parent_uuid,
                       pf=obj['RelationshipParams']['parent_function'], params=obj['RelationshipParams'])

                return new_uuid
