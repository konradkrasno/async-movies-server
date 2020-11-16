""" Provides tests for request_manager module. """

from request_manager import RequestManager


def test_request_manager_with_valid_request(loop):
    # TODO add test database
    request = "print_all_users"
    req_man = RequestManager()
    response = loop.run_until_complete(req_man.entrypoint(request))
    # TODO add assertion
    print("response:", response)
    assert type(response) == dict


def test_request_manager_with_unknown_request(loop):
    request = "unknown_request"
    req_man = RequestManager()
    response = loop.run_until_complete(req_man.entrypoint(request))
    assert response == {"answer": "Unknown request"}
