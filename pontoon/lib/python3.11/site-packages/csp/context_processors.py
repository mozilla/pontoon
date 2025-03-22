def nonce(request):
    nonce = request.csp_nonce if hasattr(request, "csp_nonce") else ""

    return {"CSP_NONCE": nonce}
