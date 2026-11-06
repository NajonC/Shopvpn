# Review-only extension to T047a/reference_service.py. Never production code.
def web_principal(admin, *, main_installation_id, main_owner_web_admin_id):
    # A trusted caller supplies the authenticated admin and explicit web binding.
    if (admin.get("tenant") != ""
            or admin.get("role") != "owner"
            or "mobile_token_id" in admin
            or type(admin.get("id")) is not int
            or type(main_owner_web_admin_id) is not int
            or main_owner_web_admin_id <= 0
            or admin["id"] != main_owner_web_admin_id):
        raise AuthorityError("forbidden")
    return Principal("web_admin", admin["id"], main_installation_id, "owner", "web")
