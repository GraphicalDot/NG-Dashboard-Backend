








class Actions(object):



    @tornado.gen.coroutine
    @staticmethod
    def actions(name_action_by, id_action_by, name_action_on, id_action_on, action, action_collection):
		action_collection.update_one({
					"name_action_by": name_action_by,
					"id_action_by": id_action_by,
					"name_action_on": name_action_on,
					"id_action_on": id_action_on,
					"action": action,
					}, upsert=True)


