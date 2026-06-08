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
            { action: 'snooze5', title: '⏰ 5 min' },
            { action: 'snooze10', title: '⏰ 10 min' },
            { action: 'snooze15', title: '⏰ 15 min' }
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
    } else if (event.action && event.action.startsWith('snooze')) {
        const mins = event.action === 'snooze5' ? 5 : event.action === 'snooze15' ? 15 : 10;
        const reminderData = event.notification.data || {};
        const body = reminderData.medicine_name
            ? `Time to take ${reminderData.medicine_name} ${reminderData.dosage || ''}`
            : (reminderData.body || 'Time to take your medicine!');
        setTimeout(() => {
            self.registration.showNotification('⏰ Snoozed Reminder', {
                body: body,
                icon: '/static/assets/hospital_logo.png',
                vibrate: [200, 100, 200, 100, 200],
                tag: 'medicine-reminder-snoozed',
                requireInteraction: true,
                data: reminderData
            });
        }, mins * 60 * 1000);
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
        const now = new Date();
        const clientTime = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
        const clientDate = now.getFullYear() + '-' + (now.getMonth()+1).toString().padStart(2,'0') + '-' + now.getDate().toString().padStart(2,'0');
        
        const response = await fetch(`/api/reminders/due-now?client_time=${clientTime}&client_date=${clientDate}`);
        if (!response.ok) return;
        const data = await response.json();
        
        if (data.reminders && data.reminders.length > 0) {
            for (const reminder of data.reminders) {
                await self.registration.showNotification('💊 Medicine Reminder', {
                    body: `Time to take ${reminder.medicine_name}${reminder.dosage ? ' — ' + reminder.dosage : ''}`,
                    icon: '/static/assets/hospital_logo.png',
                    vibrate: [200, 100, 200, 100, 200],
                    tag: `reminder-${reminder.id}`,
                    requireInteraction: true,
                    actions: [
                        { action: 'taken', title: '✅ Taken' },
                        { action: 'snooze5', title: '⏰ 5m' },
                        { action: 'snooze10', title: '⏰ 10m' },
                        { action: 'snooze15', title: '⏰ 15m' }
                    ],
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
