from django.db import models

class Selection(models.Model):
    class SelectionStatus(models.TextChoices):
        NONE = "none", "なし"
        BRIEFING = "briefing", "説明会済"
        INTERVIEW_1 = "interview_1", "1次面接"
        INTERVIEW_2 = "interview_2", "2次面接"
        INTERVIEW_3 = "interview_3", "3次面接"
        INTERVIEW_4 = "interview_4", "4次面接"
        INTERVIEW_5 = "interview_5", "5次面接"
        FINAL = "final", "最終面接"
        OFFER = "offer", "内定"
        REJECTED = "rejected", "落ちた"

    company_name = models.CharField("企業名",max_length=255)
    interview_status = models.CharField("選考状況",
        max_length=20,
        choices=SelectionStatus.choices,
        default=SelectionStatus.NONE
    )
    resume_required = models.BooleanField("履歴書あり",default=False)
    resume_submitted = models.BooleanField("履歴書",default=False)
    aptitude_test_required = models.BooleanField("適性検査あり",default=False)
    aptitude_test_taken = models.BooleanField("適性検査",default=False)
    web_test_required = models.BooleanField("webテストあり",default=False)
    web_test_taken = models.BooleanField("webテスト",default=False)
    memo = models.TextField("メモ",blank=True,null=True)
