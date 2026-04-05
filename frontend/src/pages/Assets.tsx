import { useEffect, useState } from 'react';
import { assetsAPI } from '../services/assets.service';
import { Plus, Trash2, Home, Car, TreePine, Archive } from 'lucide-react';

interface AssetEntry {
    asset_id: number;
    name: string;
    asset_type: string;
    value: number;
}

const TYPE_ICONS: Record<string, any> = {
    'Land': TreePine,
    'House': Home,
    'Automobiles': Car,
    'Others': Archive
};

export default function Assets() {
    const [assets, setAssets] = useState<AssetEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [isAdding, setIsAdding] = useState(false);
    
    const [form, setForm] = useState({
        name: '',
        asset_type: 'House',
        value: ''
    });

    const loadAssets = async () => {
        try {
            const res = await assetsAPI.getAssets();
            setAssets(res.data.data || []);
        } catch (err) {
            console.error('Failed to load assets', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAssets();
    }, []);

    const handleCreate = async () => {
        if (!form.name || !form.value) return;
        setLoading(true);
        try {
            await assetsAPI.createAsset({
                name: form.name,
                asset_type: form.asset_type,
                value: Number(form.value)
            });
            setIsAdding(false);
            setForm({ name: '', asset_type: 'House', value: '' });
            await loadAssets();
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleDelete = async (id: number) => {
        setLoading(true);
        try {
            await assetsAPI.deleteAsset(id);
            await loadAssets();
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    if (loading && assets.length === 0) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" /></div>;

    const totalValue = assets.reduce((sum, a) => sum + a.value, 0);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Your Assets</h1>
                    <p className="text-sm text-text-secondary">Manage non-liquid custom assets</p>
                </div>
                <button onClick={() => setIsAdding(!isAdding)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-all">
                    {isAdding ? 'Cancel' : <><Plus size={16} /> Add Asset</>}
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="glass-card p-5 border-primary/20">
                    <p className="text-sm text-text-secondary mb-1">Total Assets Value</p>
                    <p className="text-2xl font-bold text-primary">₹{totalValue.toLocaleString('en-IN')}</p>
                </div>
                <div className="glass-card p-5">
                    <p className="text-sm text-text-secondary mb-1">Items</p>
                    <p className="text-2xl font-bold">{assets.length}</p>
                </div>
            </div>

            {isAdding && (
                <div className="glass-card p-5 space-y-4 border-primary/30 shadow-lg shadow-primary/5">
                    <h2 className="font-semibold text-lg">Add New Asset</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Asset Name</label>
                            <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full px-3 py-2 rounded-xl bg-bg-input border border-border outline-none focus:border-primary" placeholder="e.g. Downtown Apartment" />
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Asset Type</label>
                            <select value={form.asset_type} onChange={e => setForm({ ...form, asset_type: e.target.value })} className="w-full px-3 py-2 rounded-xl bg-bg-input border border-border outline-none focus:border-primary">
                                {Object.keys(TYPE_ICONS).map(type => (
                                    <option key={type} value={type}>{type}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-text-secondary mb-1">Current Value (₹)</label>
                            <input type="number" value={form.value} onChange={e => setForm({ ...form, value: e.target.value })} className="w-full px-3 py-2 rounded-xl bg-bg-input border border-border outline-none focus:border-primary" placeholder="e.g. 5000000" />
                        </div>
                    </div>
                    <div className="flex justify-end">
                        <button onClick={handleCreate} disabled={!form.name || !form.value} className="px-6 py-2 bg-success hover:bg-success/90 text-white rounded-xl text-sm font-medium transition-colors disabled:opacity-50">Save Asset</button>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {assets.map(asset => {
                    const Icon = TYPE_ICONS[asset.asset_type] || Archive;
                    return (
                        <div key={asset.asset_id} className="relative glass-card p-5 group hover:border-primary/30 transition-all">
                            <button onClick={() => handleDelete(asset.asset_id)} className="absolute top-4 right-4 text-text-muted hover:text-danger opacity-0 group-hover:opacity-100 transition-opacity">
                                <Trash2 size={16} />
                            </button>
                            <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-4">
                                <Icon size={20} />
                            </div>
                            <h3 className="font-semibold text-lg">{asset.name}</h3>
                            <p className="text-sm text-text-secondary mb-3">{asset.asset_type}</p>
                            <div className="pt-3 border-t border-border">
                                <p className="text-xl font-bold">₹{asset.value.toLocaleString('en-IN')}</p>
                            </div>
                        </div>
                    );
                })}
                {assets.length === 0 && !isAdding && (
                    <div className="col-span-full py-16 text-center text-text-secondary border-2 border-dashed border-border rounded-xl">
                        <Archive size={40} className="mx-auto text-text-muted mb-3" />
                        <p>No assets added yet.</p>
                        <p className="text-sm text-text-muted mt-1">Click "Add Asset" to start tracking.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
