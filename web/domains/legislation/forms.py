from django.forms import ModelForm
from django_filters import CharFilter, ChoiceFilter, FilterSet

from .models import ProductLegislation


class ProductLegislationFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains", label="Legislation Name")

    is_biocidal = ChoiceFilter(
        field_name="is_biocidal",
        choices=((True, "Yes"), (False, "No")),
        lookup_expr="exact",
        label="Is Biocidal",
    )

    is_biocidal_claim = ChoiceFilter(
        field_name="is_biocidal_claim",
        choices=((True, "Yes"), (False, "No")),
        lookup_expr="exact",
        label="Is Biocidal Claim",
    )

    is_eu_cosmetics_regulation = ChoiceFilter(
        field_name="is_eu_cosmetics_regulation",
        choices=((True, "Yes"), (False, "No")),
        lookup_expr="exact",
        label="Is EU Cosmetics Regulation",
    )

    status = ChoiceFilter(
        field_name="is_active",
        choices=((True, "Current"), (False, "Archived")),
        lookup_expr="exact",
        label="Status",
    )

    class Meta:
        model = ProductLegislation
        fields = []


class ProductLegislationForm(ModelForm):
    class Meta:
        model = ProductLegislation
        fields = ["name", "is_biocidal", "is_biocidal_claim", "is_eu_cosmetics_regulation"]
        labels = {
            "name": "Legislation Name",
            "is_biocidal": "Biocidal",
            "is_biocidal_claim": "Biocidal Claim",
            "is_eu_cosmetics_regulation": "EU Cosmetics Regulation",
        }
        help_texts = {
            "is_biocidal": "Product type numbers and active ingredients must be \
                entered by the applicant when biocidal legislation is selected",
            "is_eu_cosmetics_regulation": "A 'responsible person' statement \
            may be added to the issued certificate schedule when the applicant \
            selects EU Cosmetics Regulation legislation",
        }
