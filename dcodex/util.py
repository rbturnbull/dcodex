def get_request_dict(request):
    return request.POST if request.method == "POST" else request.GET
