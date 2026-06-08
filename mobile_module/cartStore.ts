import { create } from 'zustand';

export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  category: string;
}

interface CartState {
  items: CartItem[];
  addToCart: (medicineName: string) => void;
  removeFromCart: (itemId: string) => void;
  clearCart: () => void;
  getTotalPrice: () => number;
}

// Mock medicine catalog mapping AI-recommended drugs to stock details
const MEDICINE_CATALOG: Record<string, { id: string; price: number; category: string }> = {
  'Paracetamol (500mg)': { id: 'med-001', price: 4.99, category: 'Analgesics' },
  'Ibuprofen (200mg)': { id: 'med-002', price: 5.49, category: 'NSAID' },
  'Loperamide (2mg)': { id: 'med-003', price: 6.99, category: 'Anti-Diarrheal' },
  'Cetirizine (10mg)': { id: 'med-004', price: 7.25, category: 'Antihistamine' },
  'Antacid Tablets': { id: 'med-005', price: 3.99, category: 'Antacid' },
  'Diphenhydramine': { id: 'med-006', price: 5.99, category: 'Antihistamine / Sleep Aid' },
  'Bismuth Subsalicylate': { id: 'med-007', price: 8.49, category: 'Antacid / Antidiarrheal' },
  'Dextromethorphan HBr': { id: 'med-008', price: 9.99, category: 'Cough Suppressant' }
};

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  addToCart: (medicineName: string) => {
    // Search the catalog for matching medicine names
    const normalizedName = Object.keys(MEDICINE_CATALOG).find(key => 
      key.toLowerCase().includes(medicineName.toLowerCase()) || 
      medicineName.toLowerCase().includes(key.toLowerCase())
    ) || medicineName;

    const catalogItem = MEDICINE_CATALOG[normalizedName] || { 
      id: `med-gen-${Date.now()}`, 
      price: 5.99, 
      category: 'OTC General' 
    };

    set((state) => {
      const existingItem = state.items.find(item => item.name === normalizedName);
      if (existingItem) {
        return {
          items: state.items.map(item =>
            item.name === normalizedName ? { ...item, quantity: item.quantity + 1 } : item
          )
        };
      }
      return {
        items: [
          ...state.items,
          {
            id: catalogItem.id,
            name: normalizedName,
            price: catalogItem.price,
            quantity: 1,
            category: catalogItem.category
          }
        ]
      };
    });
  },
  removeFromCart: (itemId: string) => {
    set((state) => ({
      items: state.items.filter(item => item.id !== itemId)
    }));
  },
  clearCart: () => set({ items: [] }),
  getTotalPrice: () => {
    return get().items.reduce((total, item) => total + (item.price * item.quantity), 0);
  }
}));
