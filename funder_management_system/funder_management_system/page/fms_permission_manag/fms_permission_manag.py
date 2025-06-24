# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE


import frappe
import frappe.defaults
from frappe import _
from frappe.core.doctype.doctype.doctype import (
	clear_permissions_cache,
	validate_permissions_for_doctype,
)
from frappe.exceptions import DoesNotExistError
from frappe.modules.import_file import get_file_path, read_doc_from_file
from frappe.permissions import (
	AUTOMATIC_ROLES,
	get_all_perms,
	copy_perms,
	get_linked_doctypes,
	reset_perms,
	setup_custom_perms,
	update_permission_property,
)
from frappe.utils.user import get_users_with_role as _get_user_with_role

not_allowed_in_permission_manager = ["DocType", "Patch Log", "Module Def", "Transaction Log"]


@frappe.whitelist()
def get_roles_and_doctypes():
	frappe.only_for("Fundraising Admin")

	active_domains = frappe.get_active_domains()

	# Doctypes that can be assigned
	doctypes = frappe.get_all(
		"DocType",
		filters={
			"istable": 0,
			"issingle": 0,
			"name": ["not in", not_allowed_in_permission_manager],
		},
		or_filters={
			"restrict_to_domain": ["in", active_domains],
			"restrict_to_domain": ""
		},
		fields=["name"]
	)

	# Static allowed roles
	base_roles = ["Fundraising Admin", "Budget Planner"]

	# Custom roles created by the current user
	custom_roles = frappe.get_all("Role", filters={
		"owner": frappe.session.user,
		"disabled": 0
	}, fields=["name"])

	allowed_roles = base_roles + [r.name for r in custom_roles]

	roles = frappe.get_all(
		"Role",
		filters={
			"name": ["in", allowed_roles],
			"disabled": 0
		},
		fields=["name"]
	)

	doctypes_list = [{"label": _(d["name"]), "value": d["name"]} for d in doctypes]
	roles_list = [{"label": _(r["name"]), "value": r["name"]} for r in roles]

	return {
		"doctypes": sorted(doctypes_list, key=lambda d: d["label"].casefold()),
		"roles": sorted(roles_list, key=lambda r: r["label"].casefold())
	}


@frappe.whitelist()
def get_fms_roles(doctype, txt, searchfield, start, page_len, filters):
	base_roles = ["Fundraising Admin", "Budget Planner"]

	custom_roles = frappe.get_all("Role", filters={
		"owner": frappe.session.user,
		"disabled": 0
	}, fields=["name"])

	all_roles = base_roles + [r.name for r in custom_roles]
	filtered = [r for r in all_roles if txt.lower() in r.lower()] if txt else all_roles

	return [[r, r] for r in sorted(filtered)[start:start + page_len]]







@frappe.whitelist()
def get_permissions(doctype: str | None = None, role: str | None = None):
	frappe.only_for("Fundraising Admin")

	if role:
		out = get_all_perms(role)
		if doctype:
			out = [p for p in out if p.parent == doctype]

	else:
		filters = {"parent": doctype}
		
		# Allow Fundraising Admin and their created roles
		if frappe.session.user != "Administrator":
			allowed_roles = ["Fundraising Admin", "Budget Planner"]
			custom_roles = frappe.get_all("Role", filters={"owner": frappe.session.user}, pluck="name")
			filters["role"] = ["in", allowed_roles + custom_roles]

		out = frappe.get_all("Custom DocPerm", fields="*", filters=filters, order_by="permlevel")
		
		if not out:
			out = frappe.get_all("DocPerm", fields="*", filters=filters, order_by="permlevel")

	# Attach metadata
	linked_doctypes = {}
	for d in out:
		if d.parent not in linked_doctypes:
			try:
				linked_doctypes[d.parent] = get_linked_doctypes(d.parent)
			except DoesNotExistError:
				frappe.clear_last_message()
				continue

		d.linked_doctypes = linked_doctypes[d.parent]
		if meta := frappe.get_meta(d.parent):
			d.is_submittable = meta.is_submittable
			d.in_create = meta.in_create

	return out



@frappe.whitelist()
def add(parent, role, permlevel):
	frappe.only_for("Fundraising Admin")
	add_permission(parent, role, permlevel, ignore_permissions=True)


@frappe.whitelist()
def update(doctype: str, role: str, permlevel: int, ptype: str, value=None, if_owner=0) -> str | None:
	"""Update role permission params.

	Args:
	        doctype (str): Name of the DocType to update params for
	        role (str): Role to be updated for, eg "Website Manager".
	        permlevel (int): perm level the provided rule applies to
	        ptype (str): permission type, example "read", "delete", etc.
	        value (None, optional): value for ptype, None indicates False

	Return:
	        str: Refresh flag if permission is updated successfully
	"""

	def clear_cache():
		frappe.clear_cache(doctype=doctype)

	frappe.only_for("Fundraising Admin")

	if ptype == "report" and value == "1" and if_owner == "1":
		frappe.throw(_("Cannot set 'Report' permission if 'Only If Creator' permission is set"))

	out = update_permission_property(doctype, role, permlevel, ptype, value, if_owner=if_owner)

	if ptype == "if_owner" and value == "1":
		update_permission_property(doctype, role, permlevel, "report", "0", if_owner=value)

	frappe.db.after_commit.add(clear_cache)

	return "refresh" if out else None


@frappe.whitelist()
def remove(doctype, role, permlevel, if_owner=0):
	frappe.only_for("Fundraising Admin")
	setup_custom_perms(doctype)
	custom_docperms = frappe.db.get_values(
		"Custom DocPerm", {"parent": doctype, "role": role, "permlevel": permlevel, "if_owner": if_owner}
	)
	for name in custom_docperms:
		frappe.delete_doc("Custom DocPerm", name, ignore_permissions=True, force=True)

	if not frappe.get_all("Custom DocPerm", {"parent": doctype}):
		frappe.throw(_("There must be atleast one permission rule."), title=_("Cannot Remove"))

	validate_permissions_for_doctype(doctype, for_remove=True, alert=True)


@frappe.whitelist()
def reset(doctype):
	frappe.only_for("Fundraising Admin")
	reset_perms(doctype)
	clear_permissions_cache(doctype)


@frappe.whitelist()
def get_users_with_role(role):
	frappe.only_for("Fundraising Admin")
	return _get_user_with_role(role)


@frappe.whitelist()
def get_standard_permissions(doctype):
	frappe.only_for("Fundraising Admin")
	meta = frappe.get_meta(doctype)
	if meta.custom:
		doc = frappe.get_doc("DocType", doctype)
		return [p.as_dict() for p in doc.permissions]
	else:
		# also used to setup permissions via patch
		path = get_file_path(meta.module, "DocType", doctype)
		return read_doc_from_file(path).get("permissions")


def setup_custom_perms(parent):
	"""if custom permssions are not setup for the current doctype, set them up"""
	if not frappe.db.exists("Custom DocPerm", dict(parent=parent)):
		copy_perms(parent)
		return True


def add_permission(doctype, role, permlevel=0, ptype=None, ignore_permissions=True):
	"""Add a new permission rule to the given doctype
	for the given Role and Permission Level."""

	from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype

	setup_custom_perms(doctype)

	existing = frappe.db.exists("Custom DocPerm", {
		"parent": doctype,
		"role": role,
		"permlevel": permlevel,
		"if_owner": 0
	})

	if existing:
		frappe.msgprint(
			_("Permission already exists for role '{0}' on doctype '{1}' at permlevel {2}").format(
				role, doctype, permlevel
			),
			alert=True
		)
		return

	if not ptype:
		ptype = "read"

	custom_docperm = frappe.get_doc({
		"doctype": "Custom DocPerm",
		"__islocal": 1,
		"parent": doctype,
		"parenttype": "DocType",
		"parentfield": "permissions",
		"role": role,
		"permlevel": permlevel,
		ptype: 1
	})

	custom_docperm.insert(ignore_permissions=ignore_permissions)

	validate_permissions_for_doctype(doctype)

	frappe.msgprint(
		_("Added '{0}' permission for role '{1}' on doctype '{2}' at permlevel {3}").format(
			ptype, role, doctype, permlevel
		),
		alert=True
	)

	return custom_docperm.name

