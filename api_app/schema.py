import graphene
from graphene_django import DjangoObjectType
from api_app.models import Question, Answers
from users.schema import UserType
from graphql_jwt.decorators import login_required
from django.db.models import Q

class QuestionType(DjangoObjectType):
    class Meta:
        model=Question
        filter_fields={
            'title':['icontains','istartswith'],
            'description':['icontains'],
        }

class AnswerType(DjangoObjectType):
    class Meta:
        model=Answers

class Query(graphene.ObjectType):
    questions=graphene.List(QuestionType, search=graphene.String())
    answers=graphene.List(AnswerType, question_id=graphene.Int(required=True))
    single_question=graphene.Field(QuestionType, id=graphene.Int(required=True))
    

    def resolve_questions(self, info, search=None):
        if search:
            filter=(
                Q(title__icontains=search) |
                Q(description__icontains=search)

            )
            return Question.objects.filter(filter)
        return Question.objects.all() or None

    def resolve_single_question(self, info, id):
        if id is not None:
            return Question.objects.get(pk=id)
        return None

    def resolve_answers(self, info, question_id):
        question=Question.objects.get(id=question_id)
        return Answers.objects.filter(question=question)


class CreateQuestion(graphene.Mutation):
    question=graphene.Field(QuestionType)

    class Arguments:
        title=graphene.String(required=True)
        description=graphene.String()

    @login_required
    def mutate(self, info, title, description):
        user=info.context.user
        if user.is_anonymous:
            return Exception("you Must Log In to create a question")
        question=Question(
            title=title,
            description=description,
            posted_by=user
        )
        question.save()
        return CreateQuestion(question=question)


class DeleteQuestion(graphene.Mutation):
    question=graphene.Field(QuestionType)

    class Arguments:
        question_id=graphene.Int(required=True)

    @login_required
    def mutate(self ,info, question_id):
        user=info.context.user
        question=Question.objects.get(id=question_id, posted_by=user)
        question.delete()
        success="question deleted successful"
        return 


class QuestionInput(graphene.InputObjectType):
    title=graphene.String(required=True)
    description=graphene.String(required=True)

class Update_Question(graphene.Mutation):
    question=graphene.Field(QuestionType)

    class Arguments:
        question_id=graphene.ID()
        question_update=QuestionInput(required=True)
        
       

    def mutate(self, info, question_id, question_update=None):
        user=info.context.user
        question=Question.objects.get(pk=question_id, posted_by=user)
        question.title=question_update.title
        question.description=question_update.description
        question.save()
        return Update_Question(question=question)




class ProvideAnswer(graphene.Mutation):
    question=graphene.Field(QuestionType)
    answer=graphene.Field(AnswerType)

    class Arguments:
        question_id=graphene.Int(required=True)
        answer=graphene.String()

    def mutate(self, info, question_id, answer):
        user=info.context.user
        if user.is_anonymous:
            raise Exception("you must Log In")
        question=Question.objects.get(id=question_id)
        if not question:
            raise Exception("question does not exist")
        ans=Answers.objects.create(posted_by=user, answer=answer, question=question)
        return ProvideAnswer(question=question, answer=ans)



class Mutation(graphene.ObjectType):
    create_question=CreateQuestion.Field() 
    create_answer=ProvideAnswer.Field()
    update_question=Update_Question.Field()
    deleted_question=DeleteQuestion.Field()          