from django import forms

class SeatSelectorForm(forms.Form):
    seat_select = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, seating_group):
        super().__init__()
        self.fields['seat_select'].queryset = seating_group.seat_set.all()

class SeatingGroupFormSet():
    def __init__(self, seating_group):
        self.seating_group = seating_group

    @property
    def forms(self):
        return [TicketTypeForm(seat) for seat in self.seating_group.seat_set.all()]

class TicketTypeForm(forms.Form):
    def __init__(self, seat):
        super().__init__()
        field_name = "seats[%d][ticket_type]".format(seat.id)
        self.fields[field_name] = forms.ChoiceField(
            choices=[("student", "Student"), ("normal", "Fullpris")],
            widget=forms.RadioSelect,
            required=False,
            label=seat.name
        )
        self.seat_id = seat.id
