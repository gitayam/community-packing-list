import { Suspense } from 'react';
import { Link } from 'react-router-dom';
import {
  Plus, Upload, Eye, AlertCircle, Package, CheckCircle2,
  TrendingUp, Store, GraduationCap, MapPin
} from 'lucide-react';
import { usePackingLists } from '@/hooks/usePackingLists';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ListSkeleton } from '@/components/ui/Skeleton';

function PackingListsContent() {
  const { data: packingLists, error } = usePackingLists();

  if (error) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="rounded-2xl shadow-lg overflow-hidden" style={{
          backgroundColor: 'white',
          border: '2px solid #fee2e2'
        }}>
          <div className="text-center py-12 px-6">
            {/* Icon */}
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-6" style={{
              backgroundColor: '#fef2f2'
            }}>
              <AlertCircle size={40} style={{ color: '#dc2626' }} />
            </div>

            {/* Title */}
            <h3 className="text-2xl font-bold mb-3" style={{ color: '#111827' }}>
              Unable to Load Packing Lists
            </h3>

            {/* Description */}
            <p className="text-lg mb-8" style={{ color: '#6b7280', maxWidth: '500px', margin: '0 auto 2rem' }}>
              The backend API is not available. This is expected if the Django backend hasn't been deployed yet.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
              <Link to="/list/create">
                <button className="inline-flex items-center px-6 py-3 text-base font-semibold rounded-xl transition-all duration-200 shadow-md hover:shadow-lg" style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none'
                }}>
                  <Plus size={20} className="mr-2" />
                  Create Your First List
                </button>
              </Link>
              <button
                onClick={() => window.location.reload()}
                className="inline-flex items-center px-6 py-3 text-base font-semibold rounded-xl transition-all duration-200 border" style={{
                  backgroundColor: 'white',
                  color: '#374151',
                  borderColor: '#d1d5db'
                }}
              >
                Try Again
              </button>
            </div>

            {/* Info Box */}
            <div className="p-4 rounded-xl border" style={{
              backgroundColor: '#eff6ff',
              borderColor: '#bfdbfe',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              <p className="text-sm" style={{ color: '#1e40af' }}>
                <strong>Note:</strong> To connect to a live backend, deploy the Django API using the instructions in{' '}
                <code className="px-2 py-1 rounded" style={{
                  backgroundColor: '#dbeafe',
                  fontFamily: 'monospace',
                  fontSize: '0.875rem'
                }}>
                  BACKEND_DEPLOYMENT.md
                </code>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const totalLists = packingLists?.length || 0;

  return (
    <>
      {/* Stats Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6 border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <Package className="text-blue-600" size={32} />
            <Badge variant="info" className="bg-blue-100 text-blue-700 border-blue-200">Active</Badge>
          </div>
          <div className="text-3xl font-black text-slate-900 mb-1">{totalLists}</div>
          <div className="text-sm font-medium text-slate-600">Total Lists</div>
        </div>

        <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6 border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <TrendingUp className="text-emerald-600" size={32} />
            <Badge variant="success" className="bg-emerald-100 text-emerald-700 border-emerald-200">Updated</Badge>
          </div>
          <div className="text-3xl font-black text-slate-900 mb-1">3</div>
          <div className="text-sm font-medium text-slate-600">Recent Lists</div>
        </div>

        <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6 border border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <Store className="text-purple-600" size={32} />
            <Badge variant="default" className="bg-purple-100 text-purple-700 border-purple-200">Nearby</Badge>
          </div>
          <div className="text-3xl font-black text-slate-900 mb-1">12</div>
          <div className="text-sm font-medium text-slate-600">Stores Found</div>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-black text-slate-900">Your Packing Lists</h2>
        {totalLists > 0 && (
          <Badge className="bg-slate-100 text-slate-700 border-slate-200 px-4 py-2 text-sm font-semibold">
            {totalLists} {totalLists === 1 ? 'List' : 'Lists'}
          </Badge>
        )}
      </div>

      {packingLists && packingLists.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {packingLists.map((plist, index) => (
            <Link
              key={plist.id}
              to={`/list/${plist.id}`}
              className="group animate-fadeIn"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="h-full bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-200 hover:border-blue-300 hover:-translate-y-2 cursor-pointer overflow-hidden">
                <div className="flex flex-col h-full p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors mb-3 truncate">
                        {plist.name}
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {plist.type && (
                          <Badge className="bg-blue-100 text-blue-700 border-blue-200 text-xs font-semibold">
                            {plist.type}
                          </Badge>
                        )}
                        {plist.school && (
                          <Badge className="bg-purple-100 text-purple-700 border-purple-200 text-xs font-semibold">
                            <GraduationCap size={12} className="mr-1" />
                            {plist.school.name}
                          </Badge>
                        )}
                        {plist.base && (
                          <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200 text-xs font-semibold">
                            <MapPin size={12} className="mr-1" />
                            {plist.base.name}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0 ml-4 rounded-full bg-blue-50 p-3 group-hover:bg-blue-100 transition-colors">
                      <Package className="text-blue-600" size={24} />
                    </div>
                  </div>

                  {/* Description */}
                  {plist.description && (
                    <p className="text-slate-600 mb-4 line-clamp-2 flex-1 text-sm leading-relaxed">
                      {plist.description}
                    </p>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                    <div className="flex items-center gap-2 text-sm text-slate-500 font-medium">
                      <CheckCircle2 size={16} className="text-emerald-500" />
                      <span>Ready</span>
                    </div>
                    <div className="flex items-center gap-1 text-blue-600 font-semibold text-sm group-hover:gap-2 transition-all">
                      <span>View</span>
                      <Eye size={16} />
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm p-12 border border-slate-200 text-center">
          <div className="max-w-md mx-auto">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-50 mb-6">
              <Package className="text-blue-600" size={40} />
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mb-3">No Packing Lists Yet</h3>
            <p className="text-slate-600 mb-8 leading-relaxed">
              Get started by creating your first packing list or uploading an existing one. Build your mission-ready checklist in minutes.
            </p>
            <Link to="/list/create">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all">
                <Plus size={20} className="mr-2" />
                Create Your First List
              </Button>
            </Link>
          </div>
        </div>
      )}
    </>
  );
}

export function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section - Modern Gradient */}
      <div className="relative overflow-hidden rounded-3xl mb-12 shadow-2xl" style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e40af 50%, #0f172a 100%)'
      }}>
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
          backgroundSize: '40px 40px'
        }} />
        <div className="relative px-6 py-16 md:py-24">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-8 border" style={{
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              borderColor: 'rgba(16, 185, 129, 0.3)',
              color: '#10b981'
            }}>
              <CheckCircle2 size={16} />
              <span>Mission-Ready Preparation</span>
            </div>

            {/* Heading */}
            <h1 className="text-5xl sm:text-6xl md:text-7xl font-black mb-6" style={{
              color: 'white',
              lineHeight: '1.1',
              letterSpacing: '-0.02em'
            }}>
              Pack Smart,
              <br />
              <span style={{
                background: 'linear-gradient(to right, #60a5fa, #10b981)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                Deploy Ready
              </span>
            </h1>

            {/* Description */}
            <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto leading-relaxed">
              Community-driven packing lists for military schools, training courses, and deployments.
              Get the gear you need, when you need it.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/list/create">
                <button className="inline-flex items-center px-8 py-4 text-base font-semibold rounded-2xl transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-105" style={{
                  backgroundColor: '#10b981',
                  color: 'white',
                  border: 'none'
                }}>
                  <Plus className="mr-2" size={20} />
                  Create New List
                </button>
              </Link>
              <Link to="/list/upload">
                <button className="inline-flex items-center px-8 py-4 text-base font-semibold rounded-2xl transition-all duration-200 border hover:scale-105" style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Upload className="mr-2" size={20} />
                  Upload List
                </button>
              </Link>
              <Link to="/stores">
                <button className="inline-flex items-center px-8 py-4 text-base font-semibold rounded-2xl transition-all duration-200 border hover:scale-105" style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Store className="mr-2" size={20} />
                  Find Stores
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <Suspense fallback={<ListSkeleton items={5} />}>
        <PackingListsContent />
      </Suspense>
    </div>
  );
}
