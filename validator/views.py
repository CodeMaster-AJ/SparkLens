from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.template.loader import render_to_string

import weasyprint

from .forms import IdeaForm
from .models import IdeaSubmission, AnalysisReport
from .services import call_openrouter


class HomeView(View):
    def get(self, request):
        form = IdeaForm()
        return render(request, 'validator/home.html', {'form': form})

    def post(self, request):
        form = IdeaForm(request.POST)
        if not form.is_valid():
            return render(request, 'validator/home.html', {'form': form}, status=400)

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()

        # Save submission
        submission = form.save(commit=False)
        submission.session_key = request.session.session_key
        submission.save()

        # Call AI
        try:
            analysis = call_openrouter(submission)
        except ValueError as e:
            submission.delete()
            form.add_error(None, str(e))
            return render(request, 'validator/home.html', {'form': form, 'error': str(e)}, status=503)

        # Save report
        report = AnalysisReport.objects.create(submission=submission, **analysis)

        return redirect('report_detail', pk=report.id)


class ReportDetailView(View):
    def get(self, request, pk):
        report = get_object_or_404(AnalysisReport, id=pk)
        return render(request, 'validator/report.html', {'report': report})


class ReportPDFView(View):
    def get(self, request, pk):
        report = get_object_or_404(AnalysisReport, id=pk)
        html_string = render_to_string('validator/pdf_report.html', {'report': report}, request=request)
        pdf_file = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        title_slug = report.submission.title.replace(' ', '-').lower()[:30] or 'idea'
        filename = f"idea-validator-{title_slug}.pdf"
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class HistoryView(View):
    def get(self, request):
        if not request.session.session_key:
            submissions = []
        else:
            submissions = IdeaSubmission.objects.filter(
                session_key=request.session.session_key
            ).select_related('report').order_by('-created_at')
        return render(request, 'validator/history.html', {'submissions': submissions})

    def post(self, request):
        # Clear history
        if request.session.session_key:
            IdeaSubmission.objects.filter(session_key=request.session.session_key).delete()
            request.session.flush()
        return redirect('history')


class HealthView(View):
    def get(self, request):
        return JsonResponse({'status': 'ok'})
