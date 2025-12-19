from .models import Player,Answer,Question,QuizState,Link
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse
from django.utils import timezone

# Create your views here.
def join_view(request):
    error = None

    if request.method == "POST":
        name = request.POST.get("name")

        try:
            player = Player.objects.get(name=name)
            request.session["player_id"] = player.id
            return redirect("Xmas:quiz")
        except Player.DoesNotExist:
            error = "この名前は登録されていません"

    return render(request, "app_Xmas/join.html", {
        "error": error
    })

def player_logout_view(request):
    request.session.pop("player_id", None)
    return redirect("Xmas:join")
    

def pc_view(request):
    state = QuizState.objects.first()
    question = state.current_question

    players = Player.objects.all()

    answered_player_ids = set(
        Answer.objects.filter(
            question=question
        ).values_list("player_id", flat=True)
    )

    player_status = [{
        "name": p.name,
        "answered": p.id in answered_player_ids
    } for p in players]

    return render(request, "app_Xmas/pc.html", {
        "question": question,
        "players": player_status,
        "accepting": state.is_accepting
    })


def pc_state_api(request):
    state = QuizState.objects.first()
    if not state or not state.current_question:
        return JsonResponse({"status": "no_question"})

    q = state.current_question

    remaining = q.time_limit
    if state.started_at:
        elapsed = (timezone.now() - state.started_at).total_seconds()
        remaining = max(0, q.time_limit - int(elapsed))

        # ⏱ 0秒になったら自動停止
        if remaining == 0 and state.is_accepting:
            state.is_accepting = False
            state.save()

    players = []
    for p in Player.objects.all():
        if(p.name == "admin") : continue
        ans = Answer.objects.filter(player=p, question=q).first()
        players.append({
            "name": p.name,
            "answered": bool(ans),
            "choice": ans.choice if ans else None,
            "is_correct": ans.choice == q.correct if ans else False
        })

    return JsonResponse({
        "status": "ok",
        "remaining": remaining,
        "accepting": state.is_accepting,
        "show_answer": state.show_answer,
        
        "question": {
            "id": q.id,
            "text": q.text,
            "choices": {
                "A": q.choice_a,
                "B": q.choice_b,
                "C": q.choice_c,
                "D": q.choice_d,
            },
            "correct": q.correct,
            "time_limit": q.time_limit
        },
        "players": players
    })

def quiz_view(request):
    player_id = request.session.get("player_id")
    if not player_id:
        return redirect("Xmas:join")

    player = Player.objects.get(id=player_id)
    state = QuizState.objects.first()

    if request.method == "POST":
        if not state or not state.is_accepting:
            return HttpResponse(status=204)

        already_answered = Answer.objects.filter(
            player=player,
            question=state.current_question
        ).exists()

        if not already_answered:
            Answer.objects.create(
                player=player,
                question=state.current_question,
                choice=request.POST["choice"]
            )

        return HttpResponse(status=204)  # ← ★重要

    return render(request, "app_Xmas/quiz.html", {
        "answered": False,
    })


def adminpage(request):
    state, _ = QuizState.objects.get_or_create(id=1)
    questions = Question.objects.all()

    if request.method == "POST":

        if "set_and_start" in request.POST:
            qid = request.POST["question_id"]
            state.current_question = get_object_or_404(Question, id=qid)
            state.started_at = timezone.now()
            state.is_accepting = True
            state.show_answer = False
            Answer.objects.all().delete()
            state.save()

        elif "show_answer" in request.POST:
            state.show_answer = True
            state.is_accepting = False
            state.save()

        elif "set_waiting" in request.POST:
            # 🔴 問題待機中に戻す
            state.current_question = None
            state.started_at = None
            state.is_accepting = False
            state.show_answer = False
            Answer.objects.all().delete()
            state.save()

        return redirect("Xmas:admin")

    return render(request, "app_Xmas/admin.html", {
        "state": state,
        "questions": questions
    })

def main_page(request):
    links = Link.objects.all()
    links = links.order_by("rank").distinct()  # 重複を排除して並べ替え

    return render(request, 'app_Xmas/main.html', {'links': links})

def surprisebox_view(request, name):
    player = get_object_or_404(Player, name=name)

    return render(request, "app_Xmas/surprisebox.html", {
        "player": player
    })
