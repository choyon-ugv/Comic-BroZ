import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from payments.models import Order
from users.models import Comic

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print("Webhook ValueError:", str(e))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("Webhook SignatureVerificationError:", str(e))
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata']['order_id']
        try:
            order = Order.objects.get(id=order_id)
            order.has_paid = True
            order.save()
            print(f"Order {order_id} updated: has_paid={order.has_paid}")
            # Optionally add user to purchased_by
            comic = order.comic
            comic.purchased_by.add(order.user)
        except Order.DoesNotExist:
            print(f"Order {order_id} not found")
            return HttpResponse(status=404)

    return HttpResponse(status=200)