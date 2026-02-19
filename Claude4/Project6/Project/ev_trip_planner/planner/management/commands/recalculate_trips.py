from django.core.management.base import BaseCommand
from planner.models import Trip
from planner.views import get_coordinates
from planner.utils import plan_trip, haversine_distance


class Command(BaseCommand):
    help = 'Recalculate distances and durations for all existing trips'

    def handle(self, *args, **options):
        trips = Trip.objects.all()
        updated_count = 0

        self.stdout.write(f'Found {trips.count()} trips to recalculate...')

        for trip in trips:
            # Get coordinates for the trip locations
            start_coords = get_coordinates(trip.start_location)
            end_coords = get_coordinates(trip.destination)

            # Calculate distance using haversine formula
            distance = haversine_distance(start_coords[0], start_coords[1], end_coords[0], end_coords[1])

            # Calculate duration (average 60 km/h)
            duration_minutes = int((distance / 60) * 60)

            # Store old values for comparison
            old_distance = trip.estimated_distance
            old_duration = trip.estimated_duration

            # Update the trip
            trip.start_lat = start_coords[0]
            trip.start_lng = start_coords[1]
            trip.destination_lat = end_coords[0]
            trip.destination_lng = end_coords[1]
            trip.estimated_distance = round(distance, 2)
            trip.estimated_duration = duration_minutes
            trip.save()

            updated_count += 1

            # Show what changed
            if abs(old_distance - distance) > 1:
                self.stdout.write(
                    f'Updated: {trip.start_location} to {trip.destination}\n'
                    f'  Distance: {old_distance:.2f} km to {trip.estimated_distance:.2f} km\n'
                    f'  Duration: {old_duration} min to {trip.estimated_duration} min\n'
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully recalculate {updated_count} trips!')
        )
        self.stdout.write(
            self.style.WARNING('\nNote: Charging stops and battery consumption were not recalculated.')
        )
        self.stdout.write(
            '      For full recalculation, please plan new trips.'
        )
