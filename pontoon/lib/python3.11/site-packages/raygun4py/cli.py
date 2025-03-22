import sys
from optparse import OptionParser
from raygun4py import raygunprovider


def main():
    usage = '\n  raygun4py test <apikey>'
    parser = OptionParser(usage=usage)

    options, args = parser.parse_args()

    if 'install' in args:
        if len(args) > 1:
            print("Installed API key! Now run 'raygun4py test' to check it's working")
        else:
            print('Please provide a Raygun API key!')
    elif 'test' in args:
        if len(args) > 1 and isinstance(args[1], str):
            send_test_exception(args[1])
        else:
            print('Please provide your API key')
    else:
        parser.print_help()


def send_test_exception(apikey):
    client = raygunprovider.RaygunSender(apikey)

    try:
        raise Exception("Test exception from Raygun4py3!")
    except:
        response = client.send_exception()

        if response[0] is 202:
            print("Success! Now check your Raygun dashboard at https://app.raygun.io")
        else:
            print("Something went wrong - please check your API key or contact us to get help. The response was:")
            print(response)
