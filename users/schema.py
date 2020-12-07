import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


User=get_user_model()

class UserType(DjangoObjectType):
    class Meta:
        model=User

class CreateUser(graphene.Mutation):
    user=graphene.Field(UserType)

    class Arguments:
        username=graphene.String(required=True)
        email=graphene.String(required=True)
        password=graphene.String(required=True)

    def mutate(self, info, username, email, password):
        user=User(
            username=username,
            email=email
        )
        user.set_password(password)
        user.save()
        return CreateUser(user=user)


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user=graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)



class Mutation(graphene.ObjectType):
    create_user=CreateUser.Field()


class Query(graphene.ObjectType):
    user=graphene.Field(UserType)
    all_users=graphene.List(UserType)

    def resolve_all_users(self, info):
        return User.objects.all()

    def resolve_user(self, info):
        user=info.context.user
        if user.is_anonymous:
            raise Exception('Not Logged In')
        return user