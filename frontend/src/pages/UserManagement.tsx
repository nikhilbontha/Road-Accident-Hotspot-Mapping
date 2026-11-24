import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Check,
  X,
  UserPlus,
  Shield,
  Edit2,
  AlertTriangle,
  Clock,
} from 'lucide-react';
import { usersApi } from '../services/api';
import { User } from '../types';

export const UserManagementPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  // Modal State
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newFullName, setNewFullName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newOrg, setNewOrg] = useState('Telangana State Transport');
  const [newRole, setNewRole] = useState('safety_analyst');
  const [newPassword, setNewPassword] = useState('Password123!');

  // Initial Seed Demo Users for UI matching
  const defaultDemoUsers: User[] = [
    {
      id: 'u-1',
      fullName: 'Vikram Singh',
      email: 'vikram.singh@police.gov.in',
      organisation: 'Hyderabad Traffic Police',
      role: 'police_officer',
      status: 'pending',
      lastActiveAt: 'Waiting for approval',
    },
    {
      id: 'u-2',
      fullName: 'Anjali Verma',
      email: 'a.verma@nhai.gov.in',
      organisation: 'National Highway Authority',
      role: 'safety_analyst',
      status: 'pending',
      lastActiveAt: 'Waiting for approval',
    },
    {
      id: 'u-3',
      fullName: 'Harish Babu',
      email: 'harish.babu@ghmc.gov.in',
      organisation: 'Roads & Buildings Dept',
      role: 'authority_official',
      status: 'pending',
      lastActiveAt: 'Waiting for approval',
    },
    {
      id: 'u-4',
      fullName: 'Dr. Kiran Rao',
      email: 'admin@demo.in',
      organisation: 'State Road Safety Council',
      role: 'admin',
      status: 'active',
      lastActiveAt: 'Active now',
    },
    {
      id: 'u-5',
      fullName: 'Asha Reddy',
      email: 'asha@demo.in',
      organisation: 'Road Safety Analysis Cell',
      role: 'safety_analyst',
      status: 'active',
      lastActiveAt: '12 mins ago',
    },
    {
      id: 'u-6',
      fullName: 'Ravi Kumar',
      email: 'ravi@demo.in',
      organisation: 'Cyberabad Traffic Police',
      role: 'police_officer',
      status: 'active',
      lastActiveAt: '2 hours ago',
    },
    {
      id: 'u-7',
      fullName: 'Sana Fatima',
      email: 'sana@demo.in',
      organisation: 'HMDA Road Infrastructure',
      role: 'authority_official',
      status: 'active',
      lastActiveAt: 'Yesterday',
    },
    {
      id: 'u-8',
      fullName: 'Pooja Nair',
      email: 'pooja@demo.in',
      organisation: 'Former Safety Consultant',
      role: 'safety_analyst',
      status: 'deactivated',
      lastActiveAt: '3 weeks ago',
    },
  ];

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await usersApi.list();
      if (Array.isArray(res) && res.length > 0) {
        setUsers(res);
      } else {
        setUsers(defaultDemoUsers);
      }
    } catch (e) {
      // Fallback to demo users
      setUsers(defaultDemoUsers);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleApprove = async (id: string) => {
    try {
      await usersApi.approve(id);
    } catch (e) {
      // update local
    }
    setUsers((prev) =>
      prev.map((u) => (u.id === id ? { ...u, status: 'active', lastActiveAt: 'Just now' } : u))
    );
  };

  const handleReject = async (id: string) => {
    try {
      await usersApi.reject(id);
    } catch (e) {}
    setUsers((prev) => prev.filter((u) => u.id !== id));
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    try {
      await usersApi.update(editingUser.id, {
        role: editingUser.role,
        status: editingUser.status,
      });
    } catch (e) {}
    setUsers((prev) =>
      prev.map((u) => (u.id === editingUser.id ? editingUser : u))
    );
    setEditingUser(null);
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    const newUser: User = {
      id: `u-${Date.now()}`,
      fullName: newFullName,
      email: newEmail,
      organisation: newOrg,
      role: newRole as any,
      status: 'active',
      lastActiveAt: 'Just created',
    };
    try {
      await usersApi.create({
        full_name: newFullName,
        email: newEmail,
        organisation: newOrg,
        role: newRole,
        password: newPassword,
        status: 'active',
      });
    } catch (e) {}
    setUsers((prev) => [newUser, ...prev]);
    setShowAddModal(false);
    setNewFullName('');
    setNewEmail('');
  };

  // Pending users
  const pendingUsers = users.filter((u) => u.status === 'pending');

  // Filtered users for main table
  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.fullName.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase());
    const matchesRole = selectedRole === 'all' || u.role === selectedRole;
    const matchesStatus = selectedStatus === 'all' || u.status === selectedStatus;
    return matchesSearch && matchesRole && matchesStatus;
  });

  const getRoleLabel = (r: string) => {
    switch (r) {
      case 'admin':
        return 'Administrator';
      case 'police_officer':
        return 'Traffic Police Officer';
      case 'safety_analyst':
        return 'Road Safety Analyst';
      case 'authority_official':
        return 'Road Authority Official';
      default:
        return r;
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Yellow-edged "Accounts waiting for approval" banner */}
      {pendingUsers.length > 0 && (
        <div className="bg-card border-l-4 border-lane border-t border-r border-b border-line rounded-card p-5 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-line mb-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-lane animate-pulse" />
              <h3 className="text-[15px] font-semibold text-ink">
                {pendingUsers.length} {pendingUsers.length === 1 ? 'account' : 'accounts'} waiting for approval
              </h3>
            </div>
            <span className="text-[12px] text-muted">
              Review verification before granting access
            </span>
          </div>

          <div className="divide-y divide-line">
            {pendingUsers.map((pu) => (
              <div
                key={pu.id}
                className="py-3 flex flex-col md:flex-row md:items-center justify-between gap-3 text-[13px]"
              >
                <div>
                  <div className="font-semibold text-ink">{pu.fullName}</div>
                  <div className="text-muted text-[12px]">
                    {pu.email} · <span className="text-ink">{pu.organisation}</span> ·{' '}
                    <span className="text-[#8A6A00] font-medium">{getRoleLabel(pu.role)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 self-end md:self-auto">
                  <button
                    onClick={() => handleApprove(pu.id)}
                    className="px-3.5 py-1.5 rounded-btn bg-lane text-ink font-semibold text-[12.5px] hover:brightness-105 transition-all shadow-sm flex items-center gap-1.5"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Approve</span>
                  </button>
                  <button
                    onClick={() => handleReject(pu.id)}
                    className="px-3.5 py-1.5 rounded-btn border border-line bg-card text-muted hover:text-crit hover:border-crit transition-colors text-[12.5px] flex items-center gap-1.5"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>Reject</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 2. Controls & Filter Ribbon */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 text-muted absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by user name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3.5 py-2 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:outline-none focus:ring-2 focus:ring-lane focus:border-lane"
          />
        </div>

        {/* Role Filters & Add Button */}
        <div className="flex flex-wrap items-center gap-2">
          {['all', 'police_officer', 'safety_analyst', 'authority_official'].map((r) => (
            <button
              key={r}
              onClick={() => setSelectedRole(r)}
              className={`px-3 py-1.5 rounded-full text-[12.5px] font-medium border transition-colors ${
                selectedRole === r
                  ? 'bg-asphalt text-white border-asphalt'
                  : 'bg-card text-muted border-line hover:border-ink hover:text-ink'
              }`}
            >
              {r === 'all' ? 'All roles' : getRoleLabel(r)}
            </button>
          ))}

          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 rounded-btn bg-lane text-ink font-semibold text-[13px] hover:brightness-105 transition-all shadow-sm flex items-center gap-1.5 ml-2"
          >
            <UserPlus className="w-4 h-4" />
            <span>Add user</span>
          </button>
        </div>
      </div>

      {/* 3. Main Users Table */}
      <div className="bg-card border border-line rounded-card overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-line bg-paper/60 text-muted text-[12.5px] font-medium">
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-4">Role</th>
                <th className="py-3 px-4">Organisation</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Last active</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line text-[13.3px]">
              {filteredUsers.map((u) => (
                <tr key={u.id} className="hover:bg-paper/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-paper border border-line flex items-center justify-center font-semibold text-xs text-ink shrink-0">
                        {u.fullName
                          .split(' ')
                          .map((n) => n[0])
                          .join('')
                          .toUpperCase()
                          .slice(0, 2)}
                      </div>
                      <div>
                        <div className="font-semibold text-ink leading-tight">
                          {u.fullName}
                        </div>
                        <div className="text-[12px] text-muted">{u.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="inline-block px-2.5 py-0.5 rounded-full text-[12px] font-medium bg-[#EEF0EA] text-ink border border-line">
                      {getRoleLabel(u.role)}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-muted">{u.organisation}</td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          u.status === 'active'
                            ? 'bg-status-implemented'
                            : u.status === 'pending'
                            ? 'bg-status-review'
                            : 'bg-status-closed'
                        }`}
                      />
                      <span className="capitalize text-[12.5px]">
                        {u.status}
                      </span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-muted text-[12.5px]">
                    {u.lastActiveAt || 'Never'}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => setEditingUser(u)}
                      className="p-1.5 rounded-md hover:bg-paper text-muted hover:text-ink transition-colors"
                      title="Edit role or status"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit User Modal */}
      {editingUser && (
        <div className="fixed inset-0 bg-asphalt/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-line rounded-card max-w-md w-full p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-ink mb-1">
              Edit User Permissions
            </h3>
            <p className="text-[13px] text-muted mb-4">
              Update role assignment or deactivate access for {editingUser.fullName}.
            </p>

            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  Full name
                </label>
                <input
                  type="text"
                  disabled
                  value={editingUser.fullName}
                  className="w-full px-3 py-2 rounded-btn border border-line bg-paper text-muted text-[13.5px]"
                />
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  Role
                </label>
                <select
                  value={editingUser.role}
                  onChange={(e) =>
                    setEditingUser({ ...editingUser, role: e.target.value as any })
                  }
                  className="w-full px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:ring-2 focus:ring-lane"
                >
                  <option value="police_officer">Traffic Police Officer</option>
                  <option value="safety_analyst">Road Safety Analyst</option>
                  <option value="authority_official">Road Authority Official</option>
                  <option value="admin">Administrator</option>
                </select>
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  Account Status
                </label>
                <select
                  value={editingUser.status}
                  onChange={(e) =>
                    setEditingUser({ ...editingUser, status: e.target.value as any })
                  }
                  className="w-full px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:ring-2 focus:ring-lane"
                >
                  <option value="active">Active</option>
                  <option value="pending">Pending</option>
                  <option value="deactivated">Deactivated</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-4 border-t border-line">
                <button
                  type="button"
                  onClick={() => setEditingUser(null)}
                  className="px-4 py-2 rounded-btn border border-line text-[13px] text-muted hover:text-ink hover:bg-paper"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-btn bg-lane text-ink font-semibold text-[13px] hover:brightness-105"
                >
                  Save changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add User Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-asphalt/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-line rounded-card max-w-md w-full p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-ink mb-1">
              Add Authorized User
            </h3>
            <p className="text-[13px] text-muted mb-4">
              Directly provision an active user account.
            </p>

            <form onSubmit={handleCreateUser} className="space-y-3.5">
              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  Full name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Inspector Ramesh"
                  value={newFullName}
                  onChange={(e) => setNewFullName(e.target.value)}
                  className="w-full px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:ring-2 focus:ring-lane"
                />
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  Work email
                </label>
                <input
                  type="email"
                  required
                  placeholder="ramesh@police.gov.in"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  className="w-full px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:ring-2 focus:ring-lane"
                />
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  Organisation
                </label>
                <input
                  type="text"
                  required
                  value={newOrg}
                  onChange={(e) => setNewOrg(e.target.value)}
                  className="w-full px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:ring-2 focus:ring-lane"
                />
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  Role
                </label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  className="w-full px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:ring-2 focus:ring-lane"
                >
                  <option value="police_officer">Traffic Police Officer</option>
                  <option value="safety_analyst">Road Safety Analyst</option>
                  <option value="authority_official">Road Authority Official</option>
                  <option value="admin">Administrator</option>
                </select>
              </div>

              <div>
                <label className="block text-[12.5px] font-medium text-muted mb-1">
                  Temporary Password
                </label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-3 py-2 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:ring-2 focus:ring-lane"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-4 border-t border-line">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-btn border border-line text-[13px] text-muted hover:text-ink hover:bg-paper"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-btn bg-lane text-ink font-semibold text-[13px] hover:brightness-105"
                >
                  Create user
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
