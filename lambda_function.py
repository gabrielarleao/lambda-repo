import json
import boto3
import jwt
import os

# Configuração do DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Usuarios')

# Chave secreta para o JWT
SECRET_KEY = os.getenv("JWT_SECRET", "chave-secreta")

def lambda_handler(event, context):
    print(" Evento recebido:", json.dumps(event))  # Log do evento recebido

    try:
        # Verifica se o corpo da requisição está presente
        if "body" not in event or not event["body"]:
            print(" Erro: Corpo da requisição está vazio.")
            return {"statusCode": 400, "body": json.dumps({"error": "Corpo da requisição não pode ser vazio."})}

        # Tenta fazer o parsing do JSON
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            print("Erro: JSON inválido.")
            return {"statusCode": 400, "body": json.dumps({"error": "Formato JSON inválido."})}

        cpf = body.get("cpf")
        print(f"Buscando CPF: {cpf}")

        if not cpf:
            print("Erro: CPF não foi fornecido.")
            return {"statusCode": 400, "body": json.dumps({"error": "CPF é obrigatório"})}

        # Buscar no DynamoDB
        response = table.get_item(Key={"cpf": cpf})
        user = response.get("Item")
        print(f"Resposta do DynamoDB: {json.dumps(response)}")

        if not user:
            print("Erro: CPF não encontrado.")
            return {"statusCode": 401, "body": json.dumps({"error": "CPF não encontrado"})}

        # Gerar um token JWT
        token = jwt.encode({"cpf": cpf}, SECRET_KEY, algorithm="HS256")
        print(f"Token gerado para {cpf}: {token}")

        return {
            "statusCode": 200,
            "body": json.dumps({"token": token})
        }

    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": "Erro interno no servidor"})}
