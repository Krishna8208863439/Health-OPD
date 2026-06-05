// Service Worker for Medicine Reminder Alarm Notifications
// This runs in the background even when the browser tab is closed

const CACHE_NAME = 'healthcare-sw-v1';

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

// Listen for push messages from the server (for future server-push)
self.addEventListener('push', (event) => {
    const data = event.data ? event.data.json() : {};
    const title = data.title || '💊 Medicine Reminder';
    const options = {
        body: data.body || 'Time to take your medicine!',
        icon: '/static/assets/hospital_logo.png',
        badge: '/static/assets/hospital_logo.png',
        vibrate: [200, 100, 200, 100, 200],
        tag: 'medicine-reminder',
        requireInteraction: true,
        actions: [
            { action: 'taken', title: '✅ Taken' },
            { action: 'snooze', title: '⏰ Snooze 10 min' }
        ],
        data: data
    };
    event.waitUntil(self.registration.showNotification(title, options));
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'taken') {
        // Mark as taken — open the reminders page
        event.waitUntil(
            clients.openWindow('/reminders')
        );
    } else if (event.action === 'snooze') {
        // Snooze: show again after 10 minutes
        const reminderData = event.notification.data || {};
        setTimeout(() => {
            self.registration.showNotification('⏰ Snoozed Reminder', {
                body: reminderData.body || 'Time to take your medicine!',
                icon: '/static/assets/hospital_logo.png',
                vibrate: [200, 100, 200, 100, 200],
                tag: 'medicine-reminder-snoozed',
                requireInteraction: true
            });
        }, 10 * 60 * 1000);
    } else {
        event.waitUntil(
            clients.matchAll({ type: 'window' }).then((windowClients) => {
                for (const client of windowClients) {
                    if (client.url.includes('/reminders') && 'focus' in client) {
                        return client.focus();
                    }
                }
                return clients.openWindow('/reminders');
            })
        );
    }
});

// Background Sync for checking reminders
self.addEventListener('sync', (event) => {
    if (event.tag === 'check-reminders') {
        event.waitUntil(checkRemindersInBackground());
    }
});

async function checkRemindersInBackground() {
    try {
        const response = await fetch('/api/reminders/due-now');
        if (!response.ok) return;
        const data = await response.json();
        
        if (data.reminders && data.reminders.length > 0) {
            for (const reminder of data.reminders) {
                await self.registration.showNotification('💊 Medicine Reminder', {
                    body: `Time to take: ${reminder.medicine_name} - ${reminder.dosage}`,
                    icon: '/static/assets/hospital_logo.png',
                    vibrate: [200, 100, 200, 100, 200],
                    tag: `reminder-${reminder.id}`,
                    requireInteraction: true,
                    data: reminder
                });
            }
        }
    } catch (e) {
        console.log('SW background check failed:', e);
    }
}

// Periodic background sync (fires every 1 minute while app is closed)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'medicine-alarm-check') {
        event.waitUntil(checkRemindersInBackground());
    }
});
