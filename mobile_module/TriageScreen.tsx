import React, { useReducer, useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  SafeAreaView
} from 'react-native';
import { useCartStore } from './cartStore';
import { triageReducer, initialTriageState, TriageState } from './triageStateMachine';
import { fetchTriageAssessment, LLMTriageResult } from './llmService';

export const TriageScreen: React.FC = () => {
  const [state, dispatch] = useReducer(triageReducer, initialTriageState);
  const [textInput, setTextInput] = useState('');
  const [aiResponse, setAiResponse] = useState<LLMTriageResult | null>(null);
  const [loading, setLoading] = useState(false);
  
  const scrollViewRef = useRef<ScrollView>(null);
  
  // Zustand Store integrations
  const cartItems = useCartStore((state) => state.items);
  const addToCart = useCartStore((state) => state.addToCart);
  const clearCart = useCartStore((state) => state.clearCart);
  const getTotalPrice = useCartStore((state) => state.getTotalPrice);

  // Initialize the chat on start
  useEffect(() => {
    dispatch({ type: 'START' });
  }, []);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [state.messages]);

  // Handle LLM call when state transitions to DIAGNOSING
  useEffect(() => {
    if (state.currentState === 'DIAGNOSING') {
      const runTriage = async () => {
        setLoading(true);
        try {
          const result = await fetchTriageAssessment(
            state.context.initialSymptoms,
            state.context.severity || 'mild',
            state.context.durationDays || 1,
            state.context.followUpAnswers
          );
          setAiResponse(result);
          dispatch({
            type: 'RECEIVE_DIAGNOSIS',
            suspectedAilment: result.suspected_ailment,
            medicine: result.recommended_otc_medicine,
            disclaimer: result.medical_disclaimer
          });
        } catch (err) {
          console.error("Failed to run diagnosis: ", err);
        } finally {
          setLoading(false);
        }
      };
      runTriage();
    }
  }, [state.currentState]);

  const handleSendSymptoms = () => {
    if (textInput.trim() === '') return;
    dispatch({ type: 'SUBMIT_SYMPTOMS', symptoms: textInput });
    setTextInput('');
  };

  const handleSelectSeverity = (severity: 'mild' | 'moderate' | 'severe') => {
    dispatch({ type: 'SUBMIT_SEVERITY', severity });
  };

  const handleSendDuration = (days: number) => {
    dispatch({ type: 'SUBMIT_DURATION', days });
  };

  const handleAddToCart = () => {
    if (aiResponse && aiResponse.recommended_otc_medicine && aiResponse.recommended_otc_medicine !== 'None (Seek consultation)') {
      addToCart(aiResponse.recommended_otc_medicine);
      dispatch({ type: 'ADD_TO_CART' });
    }
  };

  const handleReset = () => {
    setAiResponse(null);
    dispatch({ type: 'RESET' });
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>AI Symptom Triage & Pharmacy</Text>
          <Text style={styles.headerSubtitle}>Conversational Medical Assistant</Text>
        </View>

        {/* Chat Message Window */}
        <ScrollView
          ref={scrollViewRef}
          style={styles.chatContainer}
          contentContainerStyle={styles.chatContentContainer}
        >
          {state.messages.map((msg) => {
            const isSystem = msg.sender === 'system';
            const isAI = msg.sender === 'ai';
            const isUser = msg.sender === 'user';

            return (
              <View
                key={msg.id}
                style={[
                  styles.messageWrapper,
                  isUser ? styles.userWrapper : styles.botWrapper
                ]}
              >
                <View
                  style={[
                    styles.messageBubble,
                    isUser
                      ? styles.userBubble
                      : isAI
                      ? styles.aiBubble
                      : styles.systemBubble
                  ]}
                >
                  <Text style={[styles.messageText, isUser ? styles.userText : styles.botText]}>
                    {msg.text}
                  </Text>
                </View>
                <Text style={styles.timestamp}>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Text>
              </View>
            );
          })}

          {loading && (
            <View style={[styles.messageWrapper, styles.botWrapper]}>
              <View style={[styles.messageBubble, styles.systemBubble, styles.loadingBubble]}>
                <ActivityIndicator size="small" color="#2563EB" />
                <Text style={[styles.messageText, styles.loadingText]}>Processing clinical models...</Text>
              </View>
            </View>
          )}
        </ScrollView>

        {/* Dynamic Controls based on State Machine State */}
        <View style={styles.controlPanel}>
          {state.currentState === 'INITIAL' && (
            <View style={styles.inputRow}>
              <TextInput
                style={styles.textInput}
                placeholder="e.g. I have a throbbing headache and minor nausea..."
                value={textInput}
                onChangeText={setTextInput}
                onSubmitEditing={handleSendSymptoms}
              />
              <TouchableOpacity style={styles.sendButton} onPress={handleSendSymptoms}>
                <Text style={styles.sendButtonText}>Send</Text>
              </TouchableOpacity>
            </View>
          )}

          {state.currentState === 'ASKING_SEVERITY' && (
            <View style={styles.buttonContainer}>
              <TouchableOpacity
                style={[styles.actionButton, styles.severityMild]}
                onPress={() => handleSelectSeverity('mild')}
              >
                <Text style={styles.actionButtonText}>Mild (Annoying)</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.actionButton, styles.severityModerate]}
                onPress={() => handleSelectSeverity('moderate')}
              >
                <Text style={styles.actionButtonText}>Moderate (Disruptive)</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.actionButton, styles.severitySevere]}
                onPress={() => handleSelectSeverity('severe')}
              >
                <Text style={styles.actionButtonText}>Severe (Debilitating)</Text>
              </TouchableOpacity>
            </View>
          )}

          {state.currentState === 'ASKING_DURATION' && (
            <View style={styles.buttonContainer}>
              <TouchableOpacity style={styles.actionButton} onPress={() => handleSendDuration(1)}>
                <Text style={styles.actionButtonText}>1 Day</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionButton} onPress={() => handleSendDuration(3)}>
                <Text style={styles.actionButtonText}>2 - 3 Days</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionButton} onPress={() => handleSendDuration(5)}>
                <Text style={styles.actionButtonText}>4 - 6 Days</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionButton} onPress={() => handleSendDuration(7)}>
                <Text style={styles.actionButtonText}>7+ Days</Text>
              </TouchableOpacity>
            </View>
          )}

          {state.currentState === 'DIAGNOSED' && aiResponse && (
            <View style={styles.diagnosisActionContainer}>
              {aiResponse.recommended_otc_medicine !== 'None (Seek consultation)' ? (
                <TouchableOpacity style={styles.cartButton} onPress={handleAddToCart}>
                  <Text style={styles.cartButtonText}>
                    🛒 Add {aiResponse.recommended_otc_medicine} to Cart
                  </Text>
                </TouchableOpacity>
              ) : (
                <View style={styles.warningContainer}>
                  <Text style={styles.warningText}>
                    ⚠️ Emergency/Urgent triage triggered. Standard OTC purchase unavailable.
                  </Text>
                </View>
              )}
              <TouchableOpacity style={styles.resetButton} onPress={handleReset}>
                <Text style={styles.resetButtonText}>New Assessment</Text>
              </TouchableOpacity>
            </View>
          )}

          {state.currentState === 'COMPLETED' && (
            <View style={styles.completionContainer}>
              <Text style={styles.completionText}>✓ Medication added successfully.</Text>
              <TouchableOpacity style={styles.resetButton} onPress={handleReset}>
                <Text style={styles.resetButtonText}>Start New Diagnostic</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* E-Commerce Mobile Shopping Cart Drawer (Live State Integration) */}
        <View style={styles.cartDrawer}>
          <View style={styles.cartDrawerHeader}>
            <Text style={styles.cartDrawerTitle}>Your Mobile Cart ({cartItems.length} items)</Text>
            {cartItems.length > 0 && (
              <TouchableOpacity onPress={clearCart}>
                <Text style={styles.clearText}>Clear</Text>
              </TouchableOpacity>
            )}
          </View>
          
          {cartItems.length === 0 ? (
            <Text style={styles.emptyCartText}>No items in cart. Complete diagnostic to add meds.</Text>
          ) : (
            <View style={styles.cartSummaryRow}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.cartItemsScroll}>
                {cartItems.map((item) => (
                  <View key={item.id} style={styles.cartItemBadge}>
                    <Text style={styles.cartItemName}>{item.name}</Text>
                    <Text style={styles.cartItemQty}>x{item.quantity}</Text>
                    <Text style={styles.cartItemPrice}>${(item.price * item.quantity).toFixed(2)}</Text>
                  </View>
                ))}
              </ScrollView>
              <View style={styles.cartTotalSection}>
                <Text style={styles.totalLabel}>Total:</Text>
                <Text style={styles.totalValue}>${getTotalPrice().toFixed(2)}</Text>
              </View>
            </View>
          )}
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F8FAFC'
  },
  container: {
    flex: 1,
    justifyContent: 'space-between'
  },
  header: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    alignItems: 'center'
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#0F172A'
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2
  },
  chatContainer: {
    flex: 1,
    paddingHorizontal: 16
  },
  chatContentContainer: {
    paddingVertical: 16
  },
  messageWrapper: {
    marginBottom: 16,
    maxWidth: '80%'
  },
  userWrapper: {
    alignSelf: 'flex-end',
    alignItems: 'flex-end'
  },
  botWrapper: {
    alignSelf: 'flex-start',
    alignItems: 'flex-start'
  },
  messageBubble: {
    padding: 12,
    borderRadius: 16,
    marginBottom: 4
  },
  userBubble: {
    backgroundColor: '#2563EB',
    borderTopRightRadius: 2
  },
  aiBubble: {
    backgroundColor: '#FEF3C7',
    borderTopLeftRadius: 2,
    borderWidth: 1,
    borderColor: '#F59E0B'
  },
  systemBubble: {
    backgroundColor: '#E2E8F0',
    borderTopLeftRadius: 2
  },
  loadingBubble: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  loadingText: {
    marginLeft: 8,
    color: '#64748B'
  },
  messageText: {
    fontSize: 15,
    lineHeight: 20
  },
  userText: {
    color: '#FFFFFF'
  },
  botText: {
    color: '#0F172A'
  },
  timestamp: {
    fontSize: 10,
    color: '#94A3B8'
  },
  controlPanel: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0'
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  textInput: {
    flex: 1,
    height: 44,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 22,
    paddingHorizontal: 16,
    backgroundColor: '#F8FAFC',
    color: '#0F172A',
    fontSize: 15
  },
  sendButton: {
    marginLeft: 12,
    backgroundColor: '#2563EB',
    paddingVertical: 10,
    paddingHorizontal: 18,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center'
  },
  sendButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 14
  },
  buttonContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between'
  },
  actionButton: {
    backgroundColor: '#F1F5F9',
    borderColor: '#E2E8F0',
    borderWidth: 1,
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginBottom: 8,
    width: '48%',
    alignItems: 'center'
  },
  actionButtonText: {
    color: '#334155',
    fontWeight: '600',
    fontSize: 14
  },
  severityMild: {
    borderColor: '#86EFAC',
    backgroundColor: '#F0FDF4'
  },
  severityModerate: {
    borderColor: '#FDE047',
    backgroundColor: '#FEFCE8'
  },
  severitySevere: {
    borderColor: '#FCA5A5',
    backgroundColor: '#FEF2F2'
  },
  diagnosisActionContainer: {
    flexDirection: 'column',
    alignItems: 'center',
    width: '100%'
  },
  cartButton: {
    backgroundColor: '#10B981',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
    marginBottom: 10
  },
  cartButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 16
  },
  resetButton: {
    backgroundColor: '#FFFFFF',
    borderColor: '#2563EB',
    borderWidth: 1,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center'
  },
  resetButtonText: {
    color: '#2563EB',
    fontWeight: 'bold',
    fontSize: 14
  },
  warningContainer: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FCA5A5',
    padding: 12,
    borderRadius: 8,
    width: '100%',
    marginBottom: 10
  },
  warningText: {
    color: '#DC2626',
    fontWeight: '600',
    fontSize: 13,
    textAlign: 'center'
  },
  completionContainer: {
    alignItems: 'center'
  },
  completionText: {
    color: '#10B981',
    fontWeight: 'bold',
    fontSize: 15,
    marginBottom: 12
  },
  cartDrawer: {
    backgroundColor: '#0F172A',
    padding: 16,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16
  },
  cartDrawerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10
  },
  cartDrawerTitle: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 14
  },
  clearText: {
    color: '#EF4444',
    fontSize: 12,
    fontWeight: '600'
  },
  emptyCartText: {
    color: '#94A3B8',
    fontSize: 12,
    textAlign: 'center',
    paddingVertical: 8
  },
  cartSummaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  cartItemsScroll: {
    flex: 1,
    marginRight: 10
  },
  cartItemBadge: {
    backgroundColor: '#1E293B',
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    marginRight: 8,
    flexDirection: 'row',
    alignItems: 'center'
  },
  cartItemName: {
    color: '#E2E8F0',
    fontSize: 12,
    fontWeight: '600'
  },
  cartItemQty: {
    color: '#94A3B8',
    fontSize: 11,
    marginLeft: 6
  },
  cartItemPrice: {
    color: '#34D399',
    fontSize: 11,
    fontWeight: 'bold',
    marginLeft: 8
  },
  cartTotalSection: {
    alignItems: 'flex-end',
    minWidth: 70
  },
  totalLabel: {
    color: '#94A3B8',
    fontSize: 10
  },
  totalValue: {
    color: '#34D399',
    fontSize: 15,
    fontWeight: 'bold'
  }
});
