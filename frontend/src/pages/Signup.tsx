import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MapPin, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';
import { authApi } from '../services/api';

export const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [organisation, setOrganisation] = useState('Telangana State Police');
  const [role, setRole] = useState('police_officer');
  const [password, setPassword] = useState('');
  const [policyAgreement, setPolicyAgreement] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!fullName || !email || !password) {
      setError('Please fill in all required fields.');
      return;
    }
    if (password.length < 10) {
      setError('Password must be at least 10 characters.');
      return;
    }
    if (!policyAgreement) {
      setError('You must agree to handle accident data under departmental policy.');
      return;
    }

    setLoading(true);
    try {
      const res = await authApi.register({
        full_name: fullName,
        email,
        organisation,
        role,
        password,
        policy_agreement: policyAgreement,
      });
      setSuccessMessage(
        res.message || 'Account created. An administrator approves new accounts before you can sign in.'
      );
    } catch (err: any) {
      setError(err.message || 'Failed to create account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-card">
      {/* Left Brand Panel - Asphalt */}
      <div className="md:w-5/12 bg-asphalt text-white p-8 md:p-14 flex flex-col justify-between relative overflow-hidden">
        {/* Ambient Road Graphic */}
        <div className="absolute inset-0 pointer-events-none opacity-20 flex items-center justify-center">
          <svg className="w-[600px] h-[600px]" viewBox="0 0 400 400">
            {/* Concentric rings */}
            <circle cx="200" cy="200" r="160" fill="none" stroke="#C62F2A" strokeWidth="2" strokeDasharray="6 6" />
            <circle cx="200" cy="200" r="120" fill="none" stroke="#E2762B" strokeWidth="2" />
            <circle cx="200" cy="200" r="80" fill="none" stroke="#E7B416" strokeWidth="2" />
            <circle cx="200" cy="200" r="40" fill="none" stroke="#3E8E62" strokeWidth="2" />
            {/* Road lane */}
            <line x1="200" y1="0" x2="200" y2="400" stroke="#F5B800" strokeWidth="3" strokeDasharray="12 12" />
          </svg>
        </div>

        <div className="relative z-10">
          <div
            onClick={() => navigate('/')}
            className="flex items-center gap-3 cursor-pointer mb-12"
          >
            <div className="w-9 h-9 rounded-lg bg-lane flex items-center justify-center text-asphalt shadow-md">
              <MapPin className="w-5 h-5 text-asphalt fill-asphalt" />
            </div>
            <span className="text-[17px] font-semibold tracking-tight">
              Hotspot Mapping
            </span>
          </div>

          <h1 className="text-3xl md:text-4xl font-semibold leading-tight mb-6">
            Join your team’s road safety workspace.
          </h1>

          <div className="space-y-4 text-[14.5px] text-[#C4C9CF]">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-lane shrink-0 mt-0.5" />
              <span>See every accident and hotspot on one map</span>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-lane shrink-0 mt-0.5" />
              <span>Share cases and track what gets fixed</span>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-lane shrink-0 mt-0.5" />
              <span>Keep personal details out of your analysis</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 pt-12 text-xs text-[#8E959C]">
          Team 12 · Anurag University · Decision-Support Platform BRD-RAH-001
        </div>
      </div>

      {/* Right Form Panel - Paper / Card */}
      <div className="md:w-7/12 flex items-center justify-center p-6 md:p-14 bg-paper">
        <div className="w-full max-w-md bg-card border border-line rounded-card p-8 md:p-10 shadow-sm">
          <h2 className="text-2xl font-semibold text-ink mb-1">
            Create your account
          </h2>
          <p className="text-[13px] text-muted mb-6 leading-relaxed">
            Use your work email. An administrator approves new accounts before you can sign in.
          </p>

          {error && (
            <div className="mb-5 p-3 rounded-btn bg-[#FEE2E2] border border-[#FCA5A5] text-[#991B1B] text-[13px] flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {successMessage ? (
            <div className="space-y-4">
              <div className="p-4 rounded-btn bg-warn-bg text-warn-text text-[13.5px] border border-[#FDE68A] leading-relaxed">
                <p className="font-semibold mb-1">Registration Submitted!</p>
                {successMessage}
              </div>
              <button
                onClick={() => navigate('/login')}
                className="w-full py-2.5 rounded-btn bg-lane text-ink font-semibold text-[14px] hover:brightness-105 transition-all shadow-sm flex items-center justify-center gap-2"
              >
                <span>Go to Sign in</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1.5">
                  Full name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Asha Reddy"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:outline-none focus:ring-2 focus:ring-lane focus:border-lane"
                />
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1.5">
                  Work email
                </label>
                <input
                  type="email"
                  required
                  placeholder="name@department.gov.in"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:outline-none focus:ring-2 focus:ring-lane focus:border-lane"
                />
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1.5">
                  Organisation
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Traffic Police / NHAI"
                  value={organisation}
                  onChange={(e) => setOrganisation(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:outline-none focus:ring-2 focus:ring-lane focus:border-lane"
                />
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1.5">
                  Role
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:outline-none focus:ring-2 focus:ring-lane focus:border-lane"
                >
                  <option value="police_officer">Traffic Police Officer</option>
                  <option value="safety_analyst">Road Safety Analyst</option>
                  <option value="authority_official">Road Authority Official</option>
                </select>
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  required
                  placeholder="••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:outline-none focus:ring-2 focus:ring-lane focus:border-lane"
                />
                <span className="block text-[11.5px] text-muted mt-1">
                  At least 10 characters.
                </span>
              </div>

              <div className="pt-1">
                <label className="flex items-start gap-2.5 cursor-pointer text-[13px] text-ink select-none">
                  <input
                    type="checkbox"
                    checked={policyAgreement}
                    onChange={(e) => setPolicyAgreement(e.target.checked)}
                    className="mt-0.5 rounded border-line text-lane focus:ring-lane h-4 w-4"
                  />
                  <span>
                    I will handle accident data under my department’s policy.
                  </span>
                </label>
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-btn bg-lane text-ink font-semibold text-[14px] hover:brightness-105 active:scale-[0.99] transition-all shadow-sm disabled:opacity-50"
                >
                  {loading ? 'Submitting...' : 'Create account'}
                </button>
              </div>
            </form>
          )}

          <div className="mt-6 pt-5 border-t border-line text-center text-[13px] text-muted">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-[#8A6A00] hover:underline">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
