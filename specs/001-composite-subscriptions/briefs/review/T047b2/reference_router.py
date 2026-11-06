# Review-only executable T049 scaffold; appended to server.py in scratch.
# No business endpoints and no real deployment configuration are installed.
def create_composite_router(*, main_installation_id, main_owner_web_admin_id, public_origin):
    import hashlib
    import hmac
    from fastapi import APIRouter
    from composite import service

    async def composite_gate(request: Request):
        if request.headers.get("authorization", "").lower().startswith("bearer "):
            raise HTTPException(403, "forbidden")
        admin = await get_current_admin(request)
        require_owner(admin)
        require_main_tenant(admin)
        try:
            service.web_principal(
                admin, main_installation_id=main_installation_id,
                main_owner_web_admin_id=main_owner_web_admin_id,
            )
        except service.AuthorityError:
            raise HTTPException(403, "forbidden") from None
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            if request.headers.get("origin") != public_origin:
                raise HTTPException(403, "forbidden")
            cookie = request.cookies[COOKIE_NAME]
            expected = hmac.new(ADMIN_PANEL_SECRET.encode(),
                                b"composite-csrf-v1\0" + cookie.encode(), hashlib.sha256).hexdigest()
            supplied = request.headers.get("x-composite-csrf", "")
            if not hmac.compare_digest(expected, supplied):
                raise HTTPException(403, "forbidden")

    return APIRouter(prefix="/api/composite", dependencies=[Depends(composite_gate)])
