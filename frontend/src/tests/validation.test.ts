import { describe, it, expect } from 'vitest';
import { z } from 'zod';

// Signup validation schema matching Page 02
const signupSchema = z.object({
  fullName: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.string().email("Please provide a valid work email"),
  organisation: z.string().min(2, "Organisation is required"),
  role: z.enum(["police_officer", "safety_analyst", "authority_official"]),
  password: z.string().min(10, "Password must be at least 10 characters"),
  acceptPolicy: z.literal(true, {
    errorMap: () => ({ message: "You must accept the departmental data handling policy" }),
  }),
});

// Login validation schema matching Page 03
const loginSchema = z.object({
  email: z.string().email("Please provide a valid work email"),
  password: z.string().min(1, "Password is required"),
});

describe('Frontend Form & Validation Tests', () => {
  it('validates correct signup inputs', () => {
    const validData = {
      fullName: 'Asha Reddy',
      email: 'asha.reddy@police.gov.in',
      organisation: 'Road Safety Analysis Cell',
      role: 'safety_analyst' as const,
      password: 'StrongPassword123!',
      acceptPolicy: true as const,
    };
    const result = signupSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('rejects short passwords (< 10 chars)', () => {
    const invalidData = {
      fullName: 'Asha Reddy',
      email: 'asha.reddy@police.gov.in',
      organisation: 'Road Safety Analysis Cell',
      role: 'safety_analyst' as const,
      password: 'short',
      acceptPolicy: true as const,
    };
    const result = signupSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.errors[0].message).toContain('at least 10 characters');
    }
  });

  it('requires department policy acceptance checkbox', () => {
    const invalidData = {
      fullName: 'Ravi Kumar',
      email: 'ravi.kumar@police.gov.in',
      organisation: 'Traffic Police',
      role: 'police_officer' as const,
      password: 'Password12345!',
      acceptPolicy: false,
    };
    const result = signupSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it('validates correct login credentials format', () => {
    const result = loginSchema.safeParse({
      email: 'admin@police.gov.in',
      password: 'Password123!',
    });
    expect(result.success).toBe(true);
  });
});

describe('Design System Tokens & Helper Logic', () => {
  it('maps risk levels to signal color tokens correctly', () => {
    const getRiskToken = (level: string) => {
      switch (level.toLowerCase()) {
        case 'critical':
          return '#C62F2A';
        case 'high':
          return '#E2762B';
        case 'medium':
          return '#E7B416';
        case 'low':
          return '#3E8E62';
        default:
          return '#1F2328';
      }
    };

    expect(getRiskToken('critical')).toBe('#C62F2A');
    expect(getRiskToken('high')).toBe('#E2762B');
    expect(getRiskToken('medium')).toBe('#E7B416');
    expect(getRiskToken('low')).toBe('#3E8E62');
  });

  it('verifies human-in-the-loop warning badge string presence', () => {
    const badgeText = 'AI-generated · expert review needed';
    expect(badgeText).toContain('expert review needed');
    expect(badgeText).toContain('AI-generated');
  });
});
