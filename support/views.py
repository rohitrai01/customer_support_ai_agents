from django.shortcuts import render,get_object_or_404
import json
from django.http import JsonResponse
from .models import Conversation,Message
from orders.models import Order
from . agents import run_support_agent
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.
def chat(request,order_id):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        if not user_message:
            return JsonResponse({"error":"empty message"},status = 400)

        order = get_object_or_404(Order,id=order_id , user = request.user)
        conversation ,created = Conversation.objects.get_or_create(user = request.user , order=order)
        Message.objects.create(conversation=conversation , role ="user",content = user_message)

        reply = run_support_agent(user_message,conversation.id,order.id , request.user.id)
        Message.objects.create(conversation=conversation,role="assistant",content=reply)
    
        return JsonResponse({"reply":reply})
@staff_member_required
def dashboard(request):
    conversation = Conversation.objects.all().order_by("-created_at")
    context={
        "conversation":conversation
    }
    return render(request,"support/dashboard.html",context)


def conversation_detail(request,conversation_id):
    conversation = get_object_or_404(Conversation,id=conversation_id)
    messages = conversation.message.order_by("created_at")
    agentlogs = conversation.agentlog.order_by("created_at")

    context={
        "conversation":conversation,
        "messages":messages,
        "agentlogs":agentlogs,
    }
    return render(request,"support/conversation_detail.html",context)
