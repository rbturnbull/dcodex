from dcodex.similarity import plot_rolling_average
from django import forms
from .models import *
import io


class PlotRollingAverageForm(forms.Form):
    manuscript = forms.ModelChoiceField(
        queryset=Manuscript.objects.all(), empty_label=None
    )
    comparison_manuscripts = forms.ModelMultipleChoiceField(
        queryset=Manuscript.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def get_svg_data(self):
        # send email using the self.cleaned_data dictionary
        import matplotlib.pyplot as plt

        plt.switch_backend("Agg")
        f = io.StringIO()

        manuscript = self.cleaned_data["manuscript"]
        comparison_manuscripts = self.cleaned_data["comparison_manuscripts"]

        mss_sigla = {ms.siglum: ms.name for ms in comparison_manuscripts}

        plot_rolling_average(
            manuscript=manuscript,
            mss_sigla=mss_sigla,
        )

        plt.savefig(f, format="svg", bbox_inches="tight")
        return f.getvalue()
