
Interacting with DynamoDB with Boto3:
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/programming-with-python.html for dynamoDB

## The # noqa: E402 in testing/conftest.py
The purpose of this comment is to ignore linting here. Flake8 complains that the import is not at the top of the file (because the sys.path.append line happens before it). However, the sys.path.append is necessary for pytest to find the RetrievalInterface module. Therefore, until I can find an alternative that complies with Flake8's linting rules, I will ignore this particular concern