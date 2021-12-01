from django.db import models

# Create your models here.
class RequestInfo(models.Model):
    request_index = models.IntegerField(unique=True, primary_key=True)
    user_id = models.CharField(max_length=30)
    ori_img_path = models.CharField(max_length=100)
    result_img_path = models.CharField(max_length=100)
    detected_numbers = models.IntegerField(default=0)
    is_response = models.BooleanField(default=False)
    selected_pn_index = models.IntegerField(default=-1)
    called_number = models.CharField(max_length=15)
    timestamp1 = models.IntegerField(default=-1)
    timestamp2 = models.IntegerField(default=-1)
    timestamp3 = models.IntegerField(default=-1)
    timestamp4 = models.IntegerField(default=-1)
    root_request_index = models.IntegerField(default=-1)

    class Meta:
        ordering = ['request_index']


class DetectedNumbers(models.Model):
    detected_index = models.IntegerField(unique=True, primary_key=True)
    request_index = models.ForeignKey("RequestInfo", related_name="ex2_request_info", on_delete=models.CASCADE, db_column="request_index")
    number_index = models.IntegerField()
    is_area_code = models.BooleanField(default=False)
    n_candidates = models.IntegerField(default=0)
    pos1_x = models.FloatField()
    pos1_y = models.FloatField()
    pos2_x = models.FloatField()
    pos2_y = models.FloatField()
    pos3_x = models.FloatField()
    pos3_y = models.FloatField()
    pos4_x = models.FloatField()
    pos4_y = models.FloatField()

    class Meta:
        unique_together = (('request_index', 'number_index'),)
        ordering = ['request_index', 'number_index']

class Candidates(models.Model):
    detected_index = models.ForeignKey("DetectedNumbers", related_name="ex2_detectednumbers", on_delete=models.CASCADE, db_column="detected_index")
    candidate_index = models.IntegerField()
    number = models.CharField(max_length=15)

    class Meta:
        unique_together = (('detected_index', 'candidate_index'),)
        ordering = ['detected_index', 'candidate_index']