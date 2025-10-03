import { Suspense } from 'react';
import { Link } from 'react-router-dom';
import {
  Plus, Upload, Eye, AlertCircle, Package, CheckCircle2,
  TrendingUp, Store, GraduationCap, MapPin
} from 'lucide-react';
import { usePackingLists } from '@/hooks/usePackingLists';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ListSkeleton } from '@/components/ui/Skeleton';

function PackingListsContent() {
  const { data: packingLists, error } = usePackingLists();

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card className="border-2 border-red-100 bg-red-50/50">
          <div className="text-center py-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
              <AlertCircle size={32} className="text-red-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Unable to Load Packing Lists</h3>
            <p className="text-gray-600 mb-6">
              The backend API is not available. This is expected if the Django backend hasn't been deployed yet.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/list/create">
                <Button variant="primary" className="w-full sm:w-auto">
                  <Plus size={18} className="mr-2" />
                  Create Your First List
                </Button>
              </Link>
              <Button
                variant="secondary"
                onClick={() => window.location.reload()}
                className="w-full sm:w-auto"
              >
                Try Again
              </Button>
            </div>
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> To connect to a live backend, deploy the Django API using the instructions in <code className="bg-blue-100 px-1.5 py-0.5 rounded">BACKEND_DEPLOYMENT.md</code>
              </p>
            </div>
          </div>
        </Card>
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
    <div>
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 rounded-2xl mb-8 shadow-2xl border border-white/10">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
        <div className="relative px-6 sm:px-8 py-12 md:py-20">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-full text-sm font-semibold mb-6 border border-emerald-500/20 backdrop-blur-sm">
              <CheckCircle2 size={16} />
              <span>Mission-Ready Preparation</span>
            </div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-white mb-6 leading-tight tracking-tight">
              Pack Smart,
              <br />
              <span className="bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                Deploy Ready
              </span>
            </h1>
            <p className="text-lg md:text-xl text-slate-300 mb-10 max-w-2xl mx-auto leading-relaxed">
              Community-driven packing lists for military schools, training courses, and deployments.
              Get the gear you need, when you need it.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/list/create" className="w-full sm:w-auto">
                <Button
                  variant="success"
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 px-8 py-3 text-base font-semibold rounded-xl hover:scale-105"
                >
                  <Plus className="mr-2" size={20} />
                  Create New List
                </Button>
              </Link>
              <Link to="/list/upload" className="w-full sm:w-auto">
                <Button
                  variant="secondary"
                  className="w-full bg-white/10 hover:bg-white/20 text-white border border-white/20 backdrop-blur-md transition-all duration-300 px-8 py-3 text-base font-semibold rounded-xl hover:scale-105"
                >
                  <Upload className="mr-2" size={20} />
                  Upload List
                </Button>
              </Link>
              <Link to="/stores" className="w-full sm:w-auto">
                <Button
                  variant="secondary"
                  className="w-full bg-white/10 hover:bg-white/20 text-white border border-white/20 backdrop-blur-md transition-all duration-300 px-8 py-3 text-base font-semibold rounded-xl hover:scale-105"
                >
                  <Store className="mr-2" size={20} />
                  Find Stores
                </Button>
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
